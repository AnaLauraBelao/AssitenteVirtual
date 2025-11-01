import os
import json
import datetime
from pprint import pprint

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from src.utils.infisical import get_secret

service = build('sheets', 'v4', credentials=Credentials.from_service_account_info(json.loads(get_secret("GOOGLE_SERVICE_ACCOUNT_JSON"))))

SPREADSHEET_ID = get_secret("SPREADSHEET_ID")
spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
first_sheet_id = spreadsheet["sheets"][0]["properties"]["sheetId"]
first_sheet_title = spreadsheet["sheets"][0]["properties"]["title"]

nome = "Ana"
text = (
    "Projeto de teste123\n"
    "- 43778705 - Pedido de Venda - Editar\n"
    "- 43778708 - Pedido de Venda - Cancelar\n"
    "- 43778714 - Pedido de Venda - Envio para Produção\n"
    "- Atualizar o ambiente de produção com as atividades finalizadas"
)
LINK1 = "https://exemplo.com/link1"
LINK2 = "https://exemplo.com/link2"
LINK3 = "https://exemplo.com/link3"
LINK4 = "https://exemplo.com/link4"
text_format_runs = [
    {"startIndex": 0, "format": {"bold": True}},  # "Morota"
    {"startIndex": text.find("43778705"), "format": {"link": {"uri": LINK1}}},
    {"startIndex": text.find("43778708"), "format": {"link": {"uri": LINK2}}},
    {"startIndex": text.find("43778714"), "format": {"link": {"uri": LINK3}}},
    {"startIndex": text.find("Atualizar"), "format": {"link": {"uri": LINK4}}}
]

def get_first_sheet_id():
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    return meta["sheets"][0]["properties"]["sheetId"]

def find_row_by_name(name):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="A:A"
    ).execute()
    values = result.get("values", [])
    for i, row in enumerate(values, start=1):
        if row and row[0].strip().lower() == name.lower():
            return i
    return None

def get_column_for_today(weekday):
    weekday_index = {
        'segunda': 0,
        'terça': 1,
        'quarta': 2,
        'quinta': 3,
        'sexta': 4,
        'sábado': 5,
        'domingo': 6,
    }[weekday]
    col_index = 3 + weekday_index
    return col_index

# --- Execução ---

def alter_cell_text(name, text, text_format_runs, weekday):
    sheet_id = get_first_sheet_id()
    row = find_row_by_name(name)
    col = get_column_for_today(weekday)
    if not row:
        return f"Nome '{name}' não encontrado na coluna A."
    body = {
        "requests": [
            {
                "updateCells": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row - 1,
                        "endRowIndex": row,
                        "startColumnIndex": col - 1,
                        "endColumnIndex": col
                    },
                    "rows": [
                        {
                            "values": [
                                {
                                    "userEnteredValue": {"stringValue": text},
                                    "textFormatRuns": text_format_runs,
                                    "userEnteredFormat": {
                                        "wrapStrategy": "WRAP",
                                        "horizontalAlignment": "LEFT",
                                        "verticalAlignment": "MIDDLE",
                                        "textFormat": {
                                            "fontFamily": "Arial",
                                            "fontSize": 12
                                        }
                                    }
                                }
                            ]
                        }
                    ],
                    "fields": "userEnteredValue,userEnteredFormat,textFormatRuns"
                }
            },
            {
                "updateBorders": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row - 1,
                        "endRowIndex": row,
                        "startColumnIndex": col - 1,
                        "endColumnIndex": col
                    },
                    "top": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                    "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                    "left": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                    "right": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}}
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=body
    ).execute()

    return f"✅ Planning atualizada para {nome} ({datetime.datetime.now():%A}) com sucesso!"

# alter_cell_text(sheet_id, row, col, text, text_format_runs)