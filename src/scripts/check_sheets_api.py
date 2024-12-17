#!/usr/bin/env python3
"""
Проверка доступности Google Sheets API
"""
import logging
import os
import sys

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Путь к файлу сервисного аккаунта
        service_account_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'dashbords-373217-20faafe15e3f.json'
        )
        
        # Создаем credentials
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        # Пробуем создать сервис
        service = build('sheets', 'v4', credentials=credentials)
        
        # Если дошли до этой точки, значит API включен
        logger.info("Google Sheets API успешно подключен и готов к использованию")
        
    except Exception as e:
        logger.error(f"Ошибка при проверке Google Sheets API: {str(e)}", exc_info=True)
        logger.info("\nВозможно, API не включен. Выполните следующие шаги:")
        logger.info("1. Перейдите в Google Cloud Console")
        logger.info("2. Выберите проект 'dashbords-373217'")
        logger.info("3. Перейдите в 'APIs & Services' > 'Library'")
        logger.info("4. Найдите 'Google Sheets API'")
        logger.info("5. Нажмите 'Enable'")
        sys.exit(1)

if __name__ == "__main__":
    main()
