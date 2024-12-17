"""Скрипт для получения нового refresh token."""
import os
import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Области доступа, которые нам нужны
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

def main():
    """Main function."""
    try:
        # Используем существующий client_secret.json
        config_dir = Path(project_root) / 'config'
        client_secrets_file = config_dir / 'client_secret.json'
        
        if not client_secrets_file.exists():
            logger.error(f"Файл {client_secrets_file} не найден")
            return
            
        # Запускаем процесс авторизации
        flow = InstalledAppFlow.from_client_secrets_file(
            str(client_secrets_file), SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Получаем refresh_token
        refresh_token = creds.refresh_token
        
        logger.info(f"Новый refresh_token: {refresh_token}")
        logger.info("Скопируйте этот токен и обновите его в базе данных")
        
    except Exception as e:
        logger.error(f"Error getting new refresh token: {str(e)}")

if __name__ == "__main__":
    main()
