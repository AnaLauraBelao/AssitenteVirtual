from pprint import pprint
import pandas as pd

import requests
from base64 import b64encode
from datetime import datetime, timedelta

from src.utils.infisical import get_secret

TEAMWORK_API_URL = get_secret("TEAMWORK_API_URL")
user_pass = f'{get_secret("TEAMWORK_CLIENT_ID")}:{get_secret("TEAMWORK_CLIENT_SECRET")}'
auth = b64encode(user_pass.encode('utf-8')).decode('utf-8')


def send_request(endpoint: str, body: dict = None, type: str = "POST"):
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }
    if type == "GET":
        response = requests.get(f"{TEAMWORK_API_URL}{endpoint}", headers=headers, params=body)
        response.raise_for_status()
    elif type == "POST":
        response = requests.post(f"{TEAMWORK_API_URL}{endpoint}", headers=headers, json=body)
        response.raise_for_status()
    else:
        raise ValueError("Unsupported request type")
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
    return send_request(f"tasks/{taskId}/time.json", body=body)

# pprint(store_time_entrie('2025-10-14', '09:00', 2, 30, 'Worked on project tasks', 43736782))


def get_tasks_by_user_and_date(search_term: str, start_date: str, end_date: str, project_id: str = None):
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "searchTerm": search_term,
        "pageSize": 300,
        "searchAssignees": "true",  # mantenha como string "true" se a API exigir minúsculo
        "fields[projects]": "name,id",
        "include": "projects,columns",
    }

    if project_id is not None:
        params["projectIds"] = project_id

    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }
    return send_request("tasks.json", body=params, type="GET")


def get_task_by_id(task_id):
    params = {
        "fields[projects]": "name,id",
        "include": "projects,columns",
    }

    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }
    return send_request("tasks/"+task_id+".json", body=params, type="GET")

# pprint(get_tasks_by_user_and_date('Ana Laura', '2025-10-27', '2025-11-02', "53838"))


def get_user_by_email(email: str):
    params = {
        "searchTerm": email,
        "pageSize": 300,
    }
    json_response = send_request("people.json", body=params, type="GET")
    users = json_response.get("people", [])
    if not users:
        return []
    df = pd.DataFrame(users)
    filtered = df[df["email"] == email]
    return filtered.to_dict(orient="records")[0] if not filtered.empty else None

# pprint(get_user_by_email('ana@esfera.com.br'))