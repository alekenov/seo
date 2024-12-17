#!/usr/bin/env python3
"""
Тестирование создания и работы с Google Sheets
"""
import logging
import os
import sys
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Области доступа для Google Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

def create_services(credentials):
    """
    Создание сервисов Google Sheets и Drive
    
    Args:
        credentials: Учетные данные сервисного аккаунта
        
    Returns:
        tuple: (sheets_service, drive_service)
    """
    sheets_service = build('sheets', 'v4', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)
    return sheets_service, drive_service

def share_spreadsheet(drive_service, spreadsheet_id, email, role='reader'):
    """
    Предоставление доступа к таблице
    
    Args:
        drive_service: Google Drive service
        spreadsheet_id: ID таблицы
        email: Email пользователя
        role: Роль (reader, writer, owner)
    """
    try:
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        
        result = drive_service.permissions().create(
            fileId=spreadsheet_id,
            body=permission,
            fields='id',
            sendNotificationEmail=False
        ).execute()
        
        logger.info(f"Доступ предоставлен пользователю {email} с ролью {role}")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при предоставлении доступа: {str(e)}")
        return None

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
            scopes=SCOPES
        )
        
        # Создаем сервисы
        sheets_service, drive_service = create_services(credentials)
        
        # Создаем новую таблицу
        spreadsheet = {
            'properties': {
                'title': f'Test Spreadsheet {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            }
        }
        
        spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = spreadsheet['spreadsheetId']
        
        logger.info(f"Создана новая таблица с ID: {spreadsheet_id}")
        logger.info(f"URL таблицы: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        
        # Добавляем тестовые данные
        range_name = 'Sheet1!A1:B2'
        values = [
            ['Тест', 'Данные'],
            ['Hello', 'World']
        ]
        body = {
            'values': values
        }
        
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        logger.info(f"Обновлено ячеек: {result.get('updatedCells')}")
        
        # Предоставляем доступ к таблице
        share_spreadsheet(drive_service, spreadsheet_id, 'alekenov@gmail.com', 'writer')
        
    except Exception as e:
        logger.error(f"Ошибка при работе с Google Sheets: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
