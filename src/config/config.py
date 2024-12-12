"""
Конфигурация проекта.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

def get_config() -> Dict[str, Any]:
    """
    Получение конфигурации проекта.
    
    Returns:
        Dict с конфигурацией
    """
    # Загружаем переменные окружения из .env файла
    load_dotenv()
    
    return {
        'database': {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'name': os.getenv('DB_NAME', 'seobot'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        },
        'google': {
            'credentials_file': os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json'),
            'project_id': os.getenv('GOOGLE_PROJECT_ID', '')
        },
        'telegram': {
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID', '')
        }
    }
