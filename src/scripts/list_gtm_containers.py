"""
Скрипт для получения списка контейнеров GTM
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
        account_id = creds_manager.get_credential('gtm', 'account_id')
        service_account_path = creds_manager.get_credential('gtm', 'service_account_path')
        
        # Создаем credentials
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/tagmanager.readonly']
        )
        
        # Создаем сервис
        service = build('tagmanager', 'v2', credentials=credentials)
        
        # Получаем список контейнеров
        containers = service.accounts().containers().list(
            parent=f'accounts/{account_id}'
        ).execute()
        
        logger.info("\nСписок контейнеров:")
        for container in containers.get('container', []):
            logger.info(f"Name: {container.get('name')}")
            logger.info(f"Container ID: {container.get('containerId')} (числовой)")
            logger.info(f"Public ID: {container.get('publicId')} (GTM-*)")
            logger.info(f"Usage Context: {container.get('usageContext')}")
            logger.info("---")
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка контейнеров: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
