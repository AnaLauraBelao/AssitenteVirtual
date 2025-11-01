from datetime import datetime, timedelta
from pprint import pprint

from src.utils.teamwork.api import store_time_entrie as store_time_entrie_api, get_tasks_by_user_and_date, \
    get_task_by_id as get_task_by_id_api


def store_time_entrie(start: str, end: str, taskId: int, description: str = ""):
    if start is None or end is None:
        return {
            'status': False,
            'message': f"Data de início ou fim não informada. Tente novamente."
        }
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
    except ValueError:
        return {
            'status': False,
            'message': f"Formato de data inválido. Use o formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)."
        }

    if start_dt >= end_dt:
        return {
            'status': False,
            'message': f"A data de início deve ser anterior à data de fim."
        }

    delta = end_dt - start_dt
    total_minutes = int(delta.total_seconds() // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    time_str = start_dt.strftime("%H:%M:00")
    date_str = start_dt.strftime("%Y-%m-%d")

    return store_time_entrie_api(date_str, time_str, hours, minutes, description, taskId)


def get_week_tasks_by_user(name: str):

    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    start_date_str = start_of_week.strftime("%Y-%m-%d")
    end_date_str = end_of_week.strftime("%Y-%m-%d")

    return get_tasks_by_user_and_date(name, start_date_str, end_date_str)


def get_task_by_id(task_id: str):
    return get_task_by_id_api(task_id)