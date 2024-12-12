"""Скрипт для получения списка сайтов из Google Search Console."""
import os
import sys
from googleapiclient.discovery import build

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.utils.token_manager import TokenManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_search_console_service():
    """Получение сервиса Google Search Console."""
    token_manager = TokenManager()
    token_data = token_manager.load_token('gsc')
    if not token_data:
        raise ValueError("GSC token not found. Please run setup_auth.py first")
        
    creds = token_manager.create_credentials(token_data)
    if not creds:
        raise ValueError("Failed to create credentials from token")
        
    return build('searchconsole', 'v1', credentials=creds)

def main():
    """Main function."""
    try:
        # Инициализируем сервис
        service = get_search_console_service()
        
        # Получаем список сайтов
        sites = service.sites().list().execute()
        
        print("\nДоступные сайты в Google Search Console:")
        print("-" * 50)
        
        for site in sites.get('siteEntry', []):
            print(f"URL: {site['siteUrl']}")
            print(f"Разрешения: {site['permissionLevel']}")
            print("-" * 50)
            
    except Exception as e:
        logger.error(f"Ошибка при получении списка сайтов: {e}")
        raise

if __name__ == "__main__":
    main()
