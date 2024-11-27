from googleapiclient.discovery import build
import json
from db import insert_data_to_mysql

# Função para carregar as configurações do arquivo JSON
def load_config():
    with open('configcloud.json') as f:
        return json.load(f)

# Function to load configurations for the new spreadsheet
def load_config_new():
    with open('configcloud_new.json') as f:
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

def get_sheet_data_new():
    # Load configurations
    config = load_config_new()
    
    # Your API key (from configcloud_new.json)
    API_KEY = config['api_key']

    # The new spreadsheet ID
    SPREADSHEET_ID = config['spreadsheet_id']

    # The cell range you want to access
    RANGE_NAME = config['range_name']  # From the new config file

    # Connect to the Google Sheets service
    service = build('sheets', 'v4', developerKey=API_KEY)

    # Call the API to get the data from the new spreadsheet
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])

    return rows

