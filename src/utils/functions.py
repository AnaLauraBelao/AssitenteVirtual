from pprint import pprint

from src.enum.status_tarefa import StatusAtividade
from src.utils.azure import libera_ip as libera_ip_azure
from src.utils.teamwork import store_time_entrie
from src.utils.tmetric import get_daily_entries
from src.utils.database import Channels, Servers, ResourceGroups, Subscriptions, Rules, Atividades, Projetos
from pony.orm import db_session, select
from datetime import datetime, timedelta
import re
import unicodedata
import discord
from src.views.status_view import StatusView


async def libera_ip(rule_name: str, channel_id: str, env: str, ip: str):
    with db_session:
        channel = select(c for c in Channels if c.channel == channel_id).first()
        if not channel:
            return {
                'status': False,
                'message': f"Canal não configurado para liberação de IP."
            }

        rule = select(r for r in Rules if r.env == env and r.channel == channel).first()
        if not rule:
            return {
                'status': False,
                'message': f"Regra não encontrado para o canal e ambiente informados."
            }

        server = select(s for s in Servers if rule.server == s).first()
        if not server:
            return {
                'status': False,
                'message': f"Servidor não encontrado para o canal e ambiente informados."
            }

        resource_group = select(rg for rg in ResourceGroups if rg == server.resource_group).first()
        if not resource_group:
            return {
                'status': False,
                'message': f"Resource Group não encontrado."
            }

        subscription = select(sub for sub in Subscriptions if sub == resource_group.subscription).first()
        if not subscription:
            return {
                'status': False,
                'message': f"Subscription não encontrada."
            }

    return await libera_ip_azure(
        resource_group=resource_group.resource_group,
        server_name=server.server_name,
        subscription=subscription.subscription,
        rule_name=rule_name,
        rule_type=rule.type,
        ip=ip)

async def create_daily(interaction: discord.Interaction, date):
    entries = await get_daily_entries(date)
    if not entries:
        await interaction.edit_original_response(content="Nenhuma entrada encontrada para a data informada.")

    processed_tasks = []
    for e in entries:
        taskId = e.get("task").get("externalLink").get("issueId").replace("#", "")
        project = e.get("project", {}).get("name", "Sem projeto")
        task = e.get("task", {}).get("name", "Sem tarefa")
        note = e.get("note", "")
        start = e.get("startTime", "")
        end = e.get("endTime", "")
        tags_list = [tag.get("name", "") for tag in e.get("tags", [])]
        tags = ", ".join([tag.get("name", "") for tag in e.get("tags", [])])
        store_time_entrie(start, end, taskId, note)
        if taskId in processed_tasks:
            continue  # pula se já foi processada
        processed_tasks.append(taskId)
        if any(t in ("Daily", "Não Exibir") for t in tags_list):
            continue
        msg = (
            f"Projeto: {project}\n"
            f"Tarefa: {task}\n"
            f"Nota: {note}\n"
            f"Tags: {tags}\n"
        )
        view = StatusView(e)
        await interaction.edit_original_response(content=msg, view=view)
        timeout = await view.wait()
        # Aqui você pode salvar o status selecionado (view.value) conforme necessário
        if timeout or view.value is None:
            await interaction.edit_original_response(content="Tempo esgotado ou sem seleção.", view=None)
            break


from datetime import datetime, timedelta
from pony.orm import db_session, select

def create_weekly_report():
    hoje = datetime.now()
    inicio_semana = (hoje - timedelta(days=hoje.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    fim_semana = (hoje + timedelta(days=6 - hoje.weekday())).replace(hour=23, minute=59, second=59, microsecond=999999)

    with db_session:
        atividades = select(a for a in Atividades if inicio_semana <= a.data and a.data <= fim_semana)[:]
        projetos_nomes = {}
        for a in atividades:
            if a.id_projeto_tmetric not in projetos_nomes:
                projeto = Projetos.get(id_tmetric=a.id_projeto_tmetric)
                projetos_nomes[a.id_projeto_tmetric] = projeto.nome if projeto else "Projeto desconhecido"

        agrupado = {}
        for a in atividades:
            nome_projeto = projetos_nomes.get(a.id_projeto_tmetric, "Projeto desconhecido")
            if nome_projeto not in agrupado:
                agrupado[nome_projeto] = {}
            if a.status not in agrupado[nome_projeto]:
                agrupado[nome_projeto][a.status] = []
            agrupado[nome_projeto][a.status].append(f" - {a.nome_tarefa} \n")

    mensagens = ""
    for projeto, status_dict in agrupado.items():
        msg = f"📌 Projeto: {projeto}\n"
        for status, tarefas in status_dict.items():
            tarefas_formatadas = "\n".join(t.strip() for t in tarefas)
            status_legivel = StatusAtividade.legivel(status)
            msg += f"🛠️ Tarefas:\n{tarefas_formatadas}\n"
            msg += f"📊 Status: {status_legivel}\n"
        mensagens += msg + "\n"

    return mensagens if mensagens else "Nenhuma atividade registrada na semana."

def slugify(value: str) -> str:
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    value = re.sub(r'[\s_-]+', '-', value).strip('-')
    return value