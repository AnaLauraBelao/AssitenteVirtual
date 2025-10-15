from datetime import datetime
from pprint import pprint

from src.utils.teamwork.api import store_time_entrie as store_time_entrie_api


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