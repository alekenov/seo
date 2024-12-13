"""Скрипт для получения нового refresh token."""
import os
import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Области доступа, которые нам нужны
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

def main():
    """Main function."""
    try:
        creds = CredentialsManager()
        
        # Получаем необходимые данные
        client_id = creds.get_credential('gsc', 'client_id')
        client_secret = creds.get_credential('gsc', 'client_secret')
        auth_uri = creds.get_credential('gsc', 'auth_uri')
        token_uri = creds.get_credential('gsc', 'token_uri')
        
        # Создаем временный файл client_secrets.json
        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": auth_uri,
                "token_uri": token_uri,
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
            }
        }
        
        temp_file = "client_secrets_temp.json"
        with open(temp_file, 'w') as f:
            json.dump(client_config, f)
        
        try:
            # Запускаем процесс авторизации
            flow = InstalledAppFlow.from_client_secrets_file(
                temp_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Получаем refresh_token
            refresh_token = creds.refresh_token
            
            logger.info(f"Новый refresh_token: {refresh_token}")
            logger.info("Скопируйте этот токен и обновите его в базе данных")
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
    except Exception as e:
        logger.error(f"Error getting new refresh token: {str(e)}")

if __name__ == "__main__":
    main()
