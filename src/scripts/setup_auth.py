"""Скрипт для настройки аутентификации Google Search Console."""
import os
import sys
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

# Если вы изменяете эти области, удалите ранее сохраненный токен
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

def main():
    """Main function."""
    token_manager = TokenManager()
    credentials_manager = CredentialsManager()
    
    # Загружаем учетные данные клиента
    client_creds = credentials_manager.load_credentials('gsc')
    if not client_creds:
        logger.error("Client credentials not found. Please run import_credentials.py first")
        return
    
    # Проверяем существующий токен
    token_data = token_manager.load_token('gsc')
    creds = None
    
    if token_data:
        creds = token_manager.create_credentials(token_data)
    
    # Если нет доступных учетных данных или они недействительны, позволить пользователю войти
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Не удалось обновить токен: {e}")
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(project_root, 'config', 'client_secret.json'),
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Сохраняем токен
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'scopes': creds.scopes,
            'expiry': creds.expiry.isoformat() if creds.expiry else None
        }
        token_manager.save_token('gsc', token_data)
            
    print("Аутентификация успешно настроена!")

if __name__ == '__main__':
    main()
