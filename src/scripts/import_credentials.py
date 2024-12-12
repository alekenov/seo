"""Импорт учетных данных из файла в базу данных."""
import os
import sys
import json
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def import_credentials(credentials_file: str, service: str):
    """Импорт учетных данных из файла.
    
    Args:
        credentials_file: Путь к файлу с учетными данными
        service: Название сервиса
    """
    try:
        # Загружаем данные из файла
        with open(credentials_file, 'r') as f:
            data = json.load(f)
        
        # Извлекаем нужные данные
        installed = data.get('installed', {})
        credentials_data = {
            'client_id': installed.get('client_id'),
            'client_secret': installed.get('client_secret'),
            'token_uri': installed.get('token_uri'),
            'auth_uri': installed.get('auth_uri'),
            'redirect_uris': installed.get('redirect_uris', [])
        }
        
        # Сохраняем в базу
        manager = CredentialsManager()
        if manager.save_credentials(service, credentials_data):
            logger.info(f"Successfully imported credentials for {service}")
        else:
            logger.error(f"Failed to import credentials for {service}")
            
    except Exception as e:
        logger.error(f"Error importing credentials: {e}")
        raise

def main():
    """Main function."""
    # Путь к файлу credentials.json
    credentials_file = os.path.join(project_root, 'config', 'credentials.json')
    
    if not os.path.exists(credentials_file):
        logger.error(f"Credentials file not found: {credentials_file}")
        sys.exit(1)
    
    # Импортируем учетные данные для Google Search Console
    import_credentials(credentials_file, 'gsc')

if __name__ == '__main__':
    main()
