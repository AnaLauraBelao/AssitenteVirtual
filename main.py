from src.utils.discord import client
from src.utils.infisical import get_secret

client.run(get_secret("DISCORD_TOKEN"))