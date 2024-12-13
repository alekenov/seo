"""Скрипт для анализа позиций конкретного поискового запроса."""
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.utils.logger import setup_logger
from src.utils.token_manager import TokenManager
from dotenv import load_dotenv

logger = setup_logger(__name__)
load_dotenv()

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

def get_query_data(service, site_url: str, query: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Получение данных по запросу за указанный период.
    
    Args:
        service: Сервис Google Search Console
        site_url: URL сайта
        query: Поисковый запрос
        start_date: Начальная дата
        end_date: Конечная дата
        
    Returns:
        Dict: Данные по запросу
    """
    request = {
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d'),
        'dimensions': ['query', 'date'],
        'dimensionFilterGroups': [{
            'filters': [{
                'dimension': 'query',
                'operator': 'equals',
                'expression': query
            }]
        }],
        'rowLimit': 10
    }
    
    response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
    return response.get('rows', [])

def main():
    """Основная функция."""
    query = "доставка цветов астана"
    site_url = os.getenv('SITE_URL')
    if not site_url:
        logger.error("SITE_URL not found in environment variables")
        return
        
    service = get_search_console_service()
    
    # Получаем данные за последние 10 дней
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    
    results = get_query_data(service, site_url, query, start_date, end_date)
    
    if not results:
        logger.info(f"Нет данных для запроса '{query}' за последние 10 дней")
        return
        
    logger.info(f"\nАнализ позиций для запроса '{query}':")
    logger.info("-" * 50)
    
    # Сортируем по дате
    results.sort(key=lambda x: x['keys'][1], reverse=True)
    
    for row in results:
        date = row['keys'][1]
        logger.info(
            f"Дата: {date}, "
            f"Позиция: {row['position']:.1f}, "
            f"Клики: {row['clicks']}, "
            f"Показы: {row['impressions']}"
        )

if __name__ == "__main__":
    main()
