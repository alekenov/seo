"""
Скрипт для получения списка доступных аккаунтов GTM
"""
import os
import sys
from pathlib import Path

# Добавляем путь к корневой директории проекта
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from google.oauth2 import service_account
from googleapiclient.discovery import build
from src.utils.logger import setup_logger
from src.utils.credentials_manager import CredentialsManager

logger = setup_logger(__name__)

def main():
    try:
        # Получаем учетные данные
        creds_manager = CredentialsManager()
        service_account_path = creds_manager.get_credential('gtm', 'service_account_path')
        
        logger.info(f"Используем service account: {service_account_path}")
        
        # Создаем credentials
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/tagmanager.readonly']
        )
        
        # Создаем сервис
        service = build('tagmanager', 'v2', credentials=credentials)
        
        # Получаем список аккаунтов
        accounts = service.accounts().list().execute()
        
        logger.info("\nСписок доступных аккаунтов:")
        for account in accounts.get('account', []):
            logger.info(f"Name: {account.get('name')}")
            logger.info(f"Account ID: {account.get('accountId')}")
            logger.info(f"Fingerprint: {account.get('fingerprint')}")
            logger.info("---")
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка аккаунтов: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
