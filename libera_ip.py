import re
import asyncio
import json
import ipaddress
import shlex
from typing import Optional, Tuple, Union


# Tipos genéricos do discord.py (para não quebrar caso a importação não esteja aqui)
try:
    import discord
    from discord import Message, Interaction
except Exception:  # fallback para tipagem
    Message = object  # type: ignore
    Interaction = object  # type: ignore


async def execute_shell_command(command):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout_bytes, stderr_bytes = await process.communicate()
    stdout = stdout_bytes.decode() if stdout_bytes else ""
    stderr = stderr_bytes.decode() if stderr_bytes else ""

    if stdout:
        print(f"[stdout]\n{stdout}")
    if stderr:
        print(f"[stderr]\n{stderr}")

    return process.returncode, stdout, stderr


def _extract_ip_from_text(text: str) -> Optional[str]:
    """
    Procura um IPv4 no texto e valida com ipaddress.
    Aceita padrões antigos e variações (ex.: /libera_ip 1.2.3.4, --ip=1.2.3.4, ip:1.2.3.4 etc.).
    """
    # Captura qualquer IPv4 "parecido"
    match = re.search(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b", text)
    if not match:
        return None
    candidate = match.group(1)
    try:
        ip = ipaddress.ip_address(candidate)
        if ip.version == 4:
            return str(ip)
    except ValueError:
        return None
    return None


def _get_channel_id(ctx: Union["Message", "Interaction"]) -> Optional[str]:
    """
    Obtém o channel_id a partir de Message ou Interaction.
    """
    # Message
    if hasattr(ctx, "channel") and hasattr(ctx.channel, "id"):
        return str(ctx.channel.id)
    # Interaction
    if hasattr(ctx, "channel_id") and ctx.channel_id is not None:
        return str(ctx.channel_id)
    if hasattr(ctx, "channel") and ctx.channel is not None and hasattr(ctx.channel, "id"):
        return str(ctx.channel.id)
    return None


async def _reply(ctx: Union["Message", "Interaction"], content: str, *, ephemeral: bool = True) -> None:
    """
    Responde adequadamente a uma Message (reply) ou a uma Interaction (send_message/followup).
    """
    # Interaction
    if hasattr(ctx, "response"):
        try:
            # Se ainda não respondeu, usa response.send_message
            if not ctx.response.is_done():
                await ctx.response.send_message(content, ephemeral=ephemeral)  # type: ignore[attr-defined]
                return
        except Exception:
            pass
        # Caso já tenha respondido, usa followup
        if hasattr(ctx, "followup"):
            try:
                await ctx.followup.send(content, ephemeral=ephemeral)  # type: ignore[attr-defined]
                return
            except Exception:
                pass

    # Message
    if hasattr(ctx, "reply"):
        try:
            await ctx.reply(content)  # type: ignore[attr-defined]
            return
        except Exception:
            pass

    # Fallback: tentar enviar no canal (se existir)
    if hasattr(ctx, "channel") and hasattr(ctx.channel, "send"):
        try:
            await ctx.channel.send(content)  # type: ignore[attr-defined]
        except Exception:
            pass


async def libera_ip(
        ctx: Union["Message", "Interaction"],
        rule_name: str,
        ip: Optional[str] = None,
) -> None:
    """
    Libera o IP informado no firewall do servidor (via script ./libera_ip.sh),
    suportando tanto o padrão antigo (mensagem de texto) quanto o novo (slash command).

    Parâmetros:
    - ctx: Message ou Interaction.
    - rule_name: nome da regra a ser usada no script.
    - ip: (opcional) IP explícito. Em slash commands, passe este argumento diretamente.
           Se não informado, tenta extrair do conteúdo textual (padrão antigo).
    """
    # 1) Obter channel_id
    channel_id = _get_channel_id(ctx)
    if not channel_id:
        await _reply(ctx, "Não foi possível identificar o canal desta interação/mensagem.")
        return

    # 2) Carregar mapeamento de canais
    try:
        with open("channels.json", "r", encoding="utf-8") as channels_file:
            channels = json.load(channels_file)
    except FileNotFoundError:
        await _reply(ctx, "Arquivo channels.json não encontrado. Configure os canais antes de usar este comando.")
        return
    except json.JSONDecodeError:
        await _reply(ctx, "Falha ao ler channels.json. Verifique se o JSON está válido.")
        return

    channel_info = channels.get(str(channel_id))
    if not channel_info:
        await _reply(ctx, "Canal não configurado para liberar IPs.")
        return

    resource_group = channel_info.get("resource_group")
    server_name = channel_info.get("server_name")
    subscription = channel_info.get("subscription")

    missing = [k for k, v in [("resource_group", resource_group), ("server_name", server_name), ("subscription", subscription)] if not v]
    if missing:
        await _reply(ctx, f"Canal configurado de forma incompleta. Campos ausentes: {', '.join(missing)}.")
        return

    # 3) Determinar IP
    if not ip:
        # Padrão antigo: extrair do conteúdo da mensagem
        message_content = getattr(ctx, "content", None)
        if isinstance(message_content, str):
            ip = _extract_ip_from_text(message_content)

        # Como fallback, tentar inspecionar Interaction options (quando disponível)
        if not ip and hasattr(ctx, "data"):
            try:
                options = (ctx.data or {}).get("options")  # type: ignore[attr-defined]
                if isinstance(options, list):
                    for opt in options:
                        if isinstance(opt, dict) and opt.get("name") in ("ip", "endereco", "endereco_ip"):
                            candidate = opt.get("value")
                            if isinstance(candidate, str):
                                ip_candidate = _extract_ip_from_text(candidate) or candidate
                                try:
                                    ip_val = ipaddress.ip_address(ip_candidate)
                                    if ip_val.version == 4:
                                        ip = str(ip_val)
                                        break
                                except ValueError:
                                    pass
            except Exception:
                pass

    if not ip:
        await _reply(ctx, "IP não informado ou inválido. Informe um IPv4 válido, por exemplo: 203.0.113.42")
        return

    # 4) Validar IP final
    try:
        ip_val = ipaddress.ip_address(ip)
        if ip_val.version != 4:
            await _reply(ctx, "Apenas IPv4 é suportado no momento.")
            return
        ip = str(ip_val)
    except ValueError:
        await _reply(ctx, "Endereço IP inválido. Tente novamente com um IPv4 válido.")
        return

    # 5) Montar comando de forma segura (quoting)
    cmd = "./libera_ip.sh " \
          f"--subscription={shlex.quote(subscription)} " \
          f"--resource-group={shlex.quote(resource_group)} " \
          f"--server-name={shlex.quote(server_name)} " \
          f"--rule-name={shlex.quote(rule_name)} " \
          f"--ip={shlex.quote(ip)}"

    # 6) Executar e responder
    await _reply(ctx, f"Iniciando liberação do IP {ip}...", ephemeral=True)
    returncode, _, _ = await execute_shell_command(cmd)

    if returncode == 0:
        await _reply(ctx, f"O IP {ip} foi liberado com sucesso.")
    else:
        await _reply(ctx, f"Falha ao liberar o IP {ip}. Verifique os logs do servidor para mais detalhes.")
