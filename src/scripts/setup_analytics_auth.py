"""Скрипт для настройки аутентификации Google Analytics."""
import os
import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.utils.token_manager import TokenManager
from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Области доступа для Google Analytics
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

def main():
    """Main function."""
    token_manager = TokenManager()
    credentials_manager = CredentialsManager()
    
    # Загружаем учетные данные клиента
    client_creds = credentials_manager.load_credentials('analytics')
    if not client_creds:
        logger.error("Не найдены учетные данные для Google Analytics. Сначала добавьте их в таблицу credentials.")
        logger.info("\nТребуемые поля (аналогично GSC):")
        logger.info("- client_id: ID клиента из Google Cloud Console")
        logger.info("- client_secret: Секрет клиента из Google Cloud Console")
        logger.info("- auth_uri: https://accounts.google.com/o/oauth2/auth")
        logger.info("- token_uri: https://oauth2.googleapis.com/token")
        logger.info("- project_id: ID проекта из Google Cloud Console")
        logger.info("- credentials_file: analytics_credentials.json")
        logger.info("- site_url: ID свойства GA4 (например, 123456789)")
        return
    
    # Проверяем существующий токен
    token_data = token_manager.load_token('analytics')
    creds = None
    
    if token_data:
        creds = token_manager.create_credentials(token_data)
    
    # Если нет доступных учетных данных или они недействительны, выполняем вход
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Не удалось обновить токен: {e}")
                creds = None
        
        if not creds:
            # Создаем временный файл с учетными данными
            temp_creds_file = os.path.join(project_root, 'config', 'temp_analytics_secret.json')
            try:
                with open(temp_creds_file, 'w') as f:
                    json.dump({
                        'installed': {
                            'client_id': client_creds['client_id'],
                            'project_id': client_creds['project_id'],
                            'auth_uri': client_creds['auth_uri'],
                            'token_uri': client_creds['token_uri'],
                            'client_secret': client_creds['client_secret'],
                            'redirect_uris': ['http://localhost']
                        }
                    }, f)
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    temp_creds_file,
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
                
                # Удаляем временный файл
                os.remove(temp_creds_file)
                
            except Exception as e:
                logger.error(f"Ошибка при аутентификации: {e}")
                if os.path.exists(temp_creds_file):
                    os.remove(temp_creds_file)
                return
        
        # Сохраняем токен
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'scopes': creds.scopes,
            'expiry': creds.expiry.isoformat() if creds.expiry else None
        }
        token_manager.save_token('analytics', token_data)
            
    logger.info("Аутентификация Google Analytics успешно настроена!")

if __name__ == "__main__":
    main()
