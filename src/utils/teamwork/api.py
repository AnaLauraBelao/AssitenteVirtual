import requests
import json
from base64 import b64encode
from datetime import datetime, timedelta

from src.utils.infisical import get_secret

TEAMWORK_API_URL = get_secret("TEAMWORK_API_URL")
user_pass = f'{get_secret("TEAMWORK_CLIENT_ID")}:{get_secret("TEAMWORK_CLIENT_SECRET")}'
auth = b64encode(user_pass.encode('utf-8')).decode('utf-8')


def send_request(endpoint: str, body: dict = None):
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }
    response = requests.post(f"{TEAMWORK_API_URL}{endpoint}", headers=headers, json=body)
    response.raise_for_status()
    return response.json()


def store_time_entrie(date: str, time: str, hours: int, minutes: int, description: str, taskId: int):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    body = {
        "timelog": {
            "date": date,
            "hours": hours,
            "minutes": minutes,
            "description": description,
            "taskId": int(taskId),
            "isBillable": True,
            "userId": int(get_secret("TEAMWORK_USER_ID")),
            "time": time,
        },
    }
    print(json.dumps(body, indent=4))
    return send_request(f"tasks/{taskId}/time.json", body=body)


# store_time_entrie('2025-10-14', '09:00', 2, 30, 'Worked on project tasks', 43736782)
