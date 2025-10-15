import json
import pprint
import os

from infisical_sdk import InfisicalSDKClient


config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

client = InfisicalSDKClient(host=config.get("URL"))

client.auth.universal_auth.login(
    client_id=config.get("CLIENT_ID"),
    client_secret=config.get("CLIENT_SECRET")
)

def get_secret(secret_name: str, default: str = None) -> str:
    secret = client.secrets.get_secret_by_name(
        secret_name=secret_name,
        project_id=config.get("PROJECT_ID"),
        environment_slug=config.get("ENVIRONMENT"),
        secret_path="/"
    )
    return secret.secretValue if secret else default