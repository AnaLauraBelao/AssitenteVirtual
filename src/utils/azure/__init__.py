import asyncio
import shlex
import subprocess
import ipaddress
from pprint import pprint


async def execute_az_cli(args):
    resultado = await asyncio.to_thread(
        subprocess.run, args, capture_output=True, text=True
    )
    return resultado.returncode, resultado.stdout.strip(), resultado.stderr.strip()

async def libera_ip(resource_group, server_name, subscription, rule_name, rule_type, ip):
    missing = [k for k, v in [
        ("resource_group", resource_group),
        ("server_name", server_name),
        ("subscription", subscription)
    ] if not v]
    if missing:
        return {
            'status': False,
            'message': f"Canal configurado de forma incompleta. Campos ausentes: {', '.join(missing)}."
        }

    try:
        ip_val = ipaddress.ip_address(ip)
        if ip_val.version != 4:
            return {
                'status': False,
                'message': f"Apenas IPv4 é suportado no momento."
            }
        ip = str(ip_val)
    except ValueError:
        return {
            'status': False,
            'message': f"Endereço IP inválido. Tente novamente com um IPv4 válido."
        }

    if rule_type == "sqlserver":
        show_cmd = [
            "az", "sql", "server", "firewall-rule", "show",
            "--subscription", subscription,
            "--resource-group", resource_group,
            "--server", server_name,
            "--name", rule_name
        ]
        create_cmd = [
            "az", "sql", "server", "firewall-rule", "create",
            "--subscription", subscription,
            "--resource-group", resource_group,
            "--server", server_name,
            "--name", rule_name,
            "--start-ip-address", ip,
            "--end-ip-address", ip
        ]
        update_cmd = [
            "az", "sql", "server", "firewall-rule", "update",
            "--subscription", subscription,
            "--resource-group", resource_group,
            "--server", server_name,
            "--name", rule_name,
            "--start-ip-address", ip,
            "--end-ip-address", ip
        ]
    elif rule_type == "mysql":
        show_cmd = [
            "az", "mysql", "flexible-server", "firewall-rule", "show",
            "--subscription", subscription,
            "--resource-group", resource_group,
            "--name", server_name,
            "--rule-name", rule_name
        ]
        create_cmd = [
            "az", "mysql", "flexible-server", "firewall-rule", "create",
            "--subscription", subscription,
            "--resource-group", resource_group,
            "--name", server_name,
            "--rule-name", rule_name,
            "--start-ip-address", ip,
            "--end-ip-address", ip
        ]
        update_cmd = [
            "az", "mysql", "flexible-server", "firewall-rule", "update",
            "--subscription", subscription,
            "--resource-group", resource_group,
            "--name", server_name,
            "--rule-name", rule_name,
            "--start-ip-address", ip,
            "--end-ip-address", ip
        ]
    else:
        return {
            'status': False,
            'message': "Tipo de banco não reconhecido. Use 'sqlserver' ou 'mysql'."
        }

    show_code, show_out, show_err = await execute_az_cli(show_cmd)
    if show_code != 0 or not show_out:
        create_code, create_out, create_err = await execute_az_cli(create_cmd)
        if create_code == 0:
            return {
                'status': True,
                'message': f"O IP {ip} foi liberado com sucesso."
            }
        else:
            return {
                'status': False,
                'message': f"Erro ao liberar o IP: {create_err or create_out}"
            }
    else:
        update_code, update_out, update_err = await execute_az_cli(update_cmd)
        if update_code == 0:
            return {
                'status': True,
                'message': f"O IP {ip} foi liberado com sucesso."
            }
        else:
            return {
                'status': False,
                'message': f"Erro ao liberar o IP: {update_err or update_out}"
            }
