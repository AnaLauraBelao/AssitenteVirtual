import json
import discord
import asyncio
import subprocess
from datetime import datetime
from libera_ip import execute_shell_command, libera_ip  # Importa a função do arquivo libera_ip.py

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

TOKEN = config['TOKEN']
GUILD_ID = config['GUILD_ID']
CHANNEL_ID = config['CHANNEL_ID']
USER_ID = config['USER_ID']
DM_ID = config['DM_ID']

HALF_SECONDS_NOTIFICATION = config['HALF_SECONDS_NOTIFICATION']

intents = discord.Intents.default()
intents.message_content = True  # Ativa o acesso ao conteúdo das mensagens
intents.members = True  # Ativa o acesso às informações dos membros

client = discord.Client(intents=intents)
notified_today = False  # Para evitar notificações repetidas no mesmo dia
notification_task = None  # Armazena a tarefa de notificação


async def send_notifications(user):
    global HALF_SECONDS_NOTIFICATION
    while True:
        # Envia mensagem no chat privado
        await user.send("Atualize a Planning, print planning no Obsidian")
        await asyncio.sleep(HALF_SECONDS_NOTIFICATION)  # Espera 10 minutos

        # Envia notificação de sistema
        subprocess.run(['notify-send', 'Atualize a Planning'])
        await asyncio.sleep(HALF_SECONDS_NOTIFICATION)  # Espera 10 minutos


async def stop_notifications():
    global notification_task
    if notification_task and notification_task is not None:
        notification_task.cancel()  # Cancela a tarefa de notificação
        notification_task = None


@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')


@client.event
async def on_message(message):
    global notified_today, notification_task, GUILD_ID, CHANNEL_ID, USER_ID, DM_ID
    now = datetime.now()

    # pprint(message.guild)
    # pprint(message.channel)
    # pprint(message.author)

    # Checa se a mensagem é do usuário especificado, no canal e servidor especificado
    if (
            (message.guild is not None and message.guild.id == GUILD_ID) and
            message.channel.id == CHANNEL_ID and
            message.author.id == USER_ID
    ):
        if not notified_today or now.date() > notified_today:  # Primeiro envio do dia
            notified_today = now.date()
            user = await client.fetch_user(USER_ID)
            notification_task = asyncio.create_task(send_notifications(user))
            command = f'./open_deckboard.sh'
            await execute_shell_command(command)
        else:
            await stop_notifications()  # Desliga as notificações se o usuário mandar outra mensagem

    elif message.channel.id == DM_ID and message.author.id == USER_ID:
        await stop_notifications()  # Desliga as notificações se o usuário mandar outra mensagem

    # Chama a função libera_ip com o conteúdo da mensagem e o nome do autor
    if message.content.startswith('/libera_ip'):
        name = message.author.nick if message.author.nick else message.author.global_name
        await libera_ip(message, name)

client.run(TOKEN)
