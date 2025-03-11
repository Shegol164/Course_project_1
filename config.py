import os
from pathlib import Path

# Определение корневой директории
ROOT_DIR = Path(__file__).resolve().parent

# Пути к директориям
LOGS_DIR = ROOT_DIR / 'logs'
DATA_DIR = ROOT_DIR / 'data'
REPORTS_DIR = ROOT_DIR / 'reports'

# Пути к файлам
OPERATIONS_PATH = DATA_DIR / 'operations.xlsx'
USER_SETTINGS_PATH = DATA_DIR / 'user_settings.json'
LOG_PATH = LOGS_DIR / 'app.log'
REPORTS_PATH = REPORTS_DIR / 'reports.json'

# API-ключи
API_KEY_EXCHANGE = "https://v6.exchangerate-api.com/v6/6aea48b0e431dfeebd427982/latest/USD"
API_KEY_MARKETSTACK = "https://api.marketstack.com/v1/eod?access_key=MJPLLijE16zVF5ekv7qb0LPIX9sryqqi&symbols=AAPL"

# Создание директорий, если они не существуют
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)