"""Скрипт для получения данных из Google Search Console."""
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.utils.logger import setup_logger
from src.utils.token_manager import TokenManager

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

def fetch_search_data(service, site_url: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Получение данных из Search Console.
    
    Args:
        service: Сервис Google Search Console
        site_url: URL сайта
        start_date: Начальная дата
        end_date: Конечная дата
        
    Returns:
        List[Dict]: Список данных по запросам
    """
    request = {
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d'),
        'dimensions': ['query'],
        'rowLimit': 25000,
        'startRow': 0
    }
    
    response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
    return response.get('rows', [])

def categorize_query(query: str) -> str:
    """Категоризация поискового запроса.
    
    Args:
        query: Поисковый запрос
        
    Returns:
        str: Категория запроса
    """
    query = query.lower()
    
    # Здесь можно добавить свою логику категоризации
    if 'как' in query or 'что' in query or 'почему' in query:
        return 'информационный'
    elif 'купить' in query or 'цена' in query or 'стоимость' in query:
        return 'коммерческий'
    else:
        return 'навигационный'

def save_to_database(db: PostgresClient, data: List[Dict[str, Any]], date_collected: datetime):
    """Сохранение данных в базу.
    
    Args:
        db: Клиент базы данных
        data: Данные для сохранения
        date_collected: Дата сбора данных
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            for row in data:
                query = row['keys'][0]
                query_type = categorize_query(query)
                
                cur.execute("""
                    INSERT INTO search_queries 
                    (query, query_type, position, clicks, impressions, ctr, date_collected)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    query,
                    query_type,
                    row['position'],
                    row['clicks'],
                    row['impressions'],
                    row['ctr'],
                    date_collected.date()
                ))

def main():
    """Main function."""
    try:
        # Загружаем переменные окружения
        load_dotenv()
        
        # Получаем URL сайта из переменных окружения
        site_url = os.getenv('SITE_URL')
        if not site_url:
            raise ValueError("SITE_URL not found in environment variables")
        
        # Инициализируем сервис
        service = get_search_console_service()
        
        # Получаем данные за вчера
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        # Получаем данные из Search Console
        data = fetch_search_data(service, site_url, start_date, end_date)
        
        if data:
            # Сохраняем в базу
            db = PostgresClient()
            save_to_database(db, data, end_date)
            logger.info(f"Successfully saved {len(data)} search queries")
        else:
            logger.warning("No data received from Search Console")
            
    except Exception as e:
        logger.error(f"Error fetching search data: {e}")
        raise

if __name__ == "__main__":
    main()
