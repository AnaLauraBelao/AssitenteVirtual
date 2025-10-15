import requests
from datetime import datetime, timedelta

from src.utils.infisical import get_secret

TMETRIC_API_URL = get_secret("TMETRIC_API_URL", "https://app.tmetric.com/api/v3")
TMETRIC_TOKEN = get_secret("TMETRIC_TOKEN")

def send_request(endpoint: str, params: dict = None):
    headers = {
        "Authorization": f"Bearer {TMETRIC_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{TMETRIC_API_URL}{endpoint}", headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_daily_time_entries(date: str = None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    params = {
        "startDate": date,
        "endDate": date
    }
    return send_request(f"accounts/{get_secret('TMETRIC_USER_ID')}/timeentries", params=params)