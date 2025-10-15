from typing import Any

import discord
import sqlite3
from datetime import datetime, timedelta


from src.utils.tmetric.api import get_daily_time_entries

async def get_daily_entries(date: str = None) -> Any:
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    return get_daily_time_entries(date)
