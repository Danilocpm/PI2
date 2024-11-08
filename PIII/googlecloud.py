from googleapiclient.discovery import build
import json
from db import insert_data_to_mysql

# Função para carregar as configurações do arquivo JSON
def load_config():
    with open('configcloud.json') as f:
        return json.load(f)

# Função para obter dados da Google Sheets
def get_sheet_data():
    # Carregar configurações
    config = load_config()
    
    # Sua chave de API (vinda do arquivo configcloud.json)
    API_KEY = config['api_key']

    # O ID da planilha (extraído da URL da planilha)
    SPREADSHEET_ID = config['spreadsheet_id']

    # O intervalo de células que você deseja acessar
    RANGE_NAME = config['range_name']  # Vindo do arquivo de configuração

    # Conectar ao serviço do Google Sheets
    service = build('sheets', 'v4', developerKey=API_KEY)

    # Chamar a API para obter os dados
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])

    return rows

