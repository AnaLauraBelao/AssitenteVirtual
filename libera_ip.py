import re
import asyncio
from pprint import pprint
import json

async def execute_shell_command(command):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')

async def libera_ip(message, rule_name):
    with open('channels.json', 'r') as channels_file:
        channels = json.load(channels_file)
    message_content = message.content
    channel_id = str(message.channel.id)
    ip_match = re.search(r'/libera_ip\s+(\d+\.\d+\.\d+\.\d+)', message_content)
    channel_info = channels.get(channel_id)
    if not channel_info:
        return await message.reply('Canal não configurado para liberar IPs.')
    resource_group = channel_info['resource_group']
    server_name = channel_info['server_name']
    subscription = channel_info['subscription']
    if ip_match:
        ip = ip_match.group(1)
        command = f'./libera_ip.sh --subscription={subscription} --resource-group={resource_group} --server-name={server_name} --rule-name="{rule_name}" --ip={ip}'
        pprint(command)
        await execute_shell_command(command)
        await message.reply(f'O IP {ip} foi liberado com sucesso.')