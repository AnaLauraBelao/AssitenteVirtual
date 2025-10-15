from pprint import pprint

import discord
from pony.orm import db_session
from pony.orm import select
from src.enum.status_tarefa import StatusAtividade

class StatusView(discord.ui.View):
    def __init__(self, entry):
        super().__init__(timeout=60)
        self.value = None
        self.entry = entry

    @discord.ui.select(
        placeholder="Selecione o status...",
        options=[
            discord.SelectOption(label=status.legivel(status.value), value=status.value)
            for status in StatusAtividade
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.value = select.values[0]
        entry = self.entry
        id_tmetric = entry.get("id")
        id_projeto_tmetric = entry.get("project", {}).get("id")
        data = entry.get("startTime", "")[:10]
        status = self.value
        nome_projeto = entry.get("project", {}).get("name", "Projeto desconhecido")
        id_teamwork = entry.get("task").get("externalLink").get("issueId").replace("#", "")
        nome_tarefa = entry.get("task", {}).get("name", "Tarefa Desconhecida")
        save_or_update_projeto(id_projeto_tmetric, nome_projeto)
        save_or_update_atividade(id_tmetric, id_teamwork, id_projeto_tmetric, nome_tarefa, data, status)
        await interaction.response.edit_message(content="Status salvo com sucesso!", view=None)
        self.stop()

def save_or_update_atividade(id_tmetric, id_teamwork, id_projeto_tmetric, nome_tarefa, data, status):
    from src.utils.database import Atividades, Projetos  # Importe as entidades corretas
    with db_session:
        atividade = select(a for a in Atividades if a.id_teamwork == id_teamwork).first()
        pprint(atividade)
        if atividade:
            atividade.status = status
            atividade.data = data
        else:
            projeto = select(p for p in Projetos if p.id_tmetric == id_projeto_tmetric).first()
            Atividades(
                id_tmetric=id_tmetric,
                id_teamwork=id_teamwork,
                id_projeto_tmetric=id_projeto_tmetric,
                nome_tarefa=nome_tarefa,
                data=data,
                status=status,
                projeto=projeto
            )

def save_or_update_projeto(id_tmetric, nome):
    from src.utils.database import Projetos
    with db_session:
        projeto = select(p for p in Projetos if p.id_tmetric == id_tmetric).first()
        if projeto:
            projeto.nome = nome
        else:
            Projetos(id_tmetric=id_tmetric, nome=nome)