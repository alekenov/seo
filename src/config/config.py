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
    
    # Прямое подключение к Supabase PostgreSQL
    db_url = "postgresql://postgres.jvfjxlpplbyrafasobzl:fogdif-7voHxi-ryfqug@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
    
    # Парсим URL для получения параметров подключения
    from urllib.parse import urlparse
    parsed = urlparse(db_url)
    
    return {
        'database': {
            'host': parsed.hostname,
            'port': parsed.port,
            'name': parsed.path[1:],  # Убираем начальный /
            'user': parsed.username,
            'password': parsed.password,
            'direct_url': db_url
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
