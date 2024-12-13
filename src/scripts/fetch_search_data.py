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
        'dimensions': ['query', 'page'],
        'rowLimit': 5000,  # Получаем больше данных для последующей фильтрации
    }
    
    logger.info(f"Fetching search data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
    rows = response.get('rows', [])
    
    # Фильтруем и сортируем данные
    filtered_rows = [row for row in rows if row.get('clicks', 0) > 0]
    sorted_rows = sorted(
        filtered_rows,
        key=lambda x: (x.get('clicks', 0), x.get('impressions', 0)),
        reverse=True
    )
    
    # Возвращаем только топ-50 запросов
    return sorted_rows[:50]

def categorize_query(query: str) -> str:
    """Категоризация поискового запроса.
    
    Args:
        query: Поисковый запрос
        
    Returns:
        str: Категория запроса
    """
    query = query.lower().strip()
    
    # Список основных городов Казахстана
    major_cities = {
        'алматы': 'almaty',
        'астана': 'astana',
        'шымкент': 'shymkent',
        'караганда': 'karaganda',
        'актау': 'aktau',
        'атырау': 'atyrau',
        'актобе': 'aktobe',
        'костанай': 'kostanay',
        'павлодар': 'pavlodar',
        'усть-каменогорск': 'ust-kamenogorsk',
        'семей': 'semey',
        'кызылорда': 'kyzylorda'
    }
    
    # Определяем город
    city = None
    for city_name in major_cities:
        if city_name in query:
            city = major_cities[city_name]
            break
    
    # Определяем тип запроса
    query_types = []
    
    # Доставка цветов
    if 'доставка' in query or 'заказать' in query:
        query_types.append('delivery')
        
    # Покупка цветов
    if 'купить' in query or 'цена' in query or 'стоимость' in query:
        query_types.append('purchase')
        
    # Типы цветов
    flowers = ['розы', 'тюльпаны', 'пионы', 'хризантемы', 'букет']
    for flower in flowers:
        if flower in query:
            query_types.append('flowers')
            break
            
    # Если город определен
    if city:
        if query_types:
            # Объединяем типы запроса с городом
            return f"{'+'.join(query_types)}_{city}"
        else:
            # Если тип не определен, но есть город
            return f"general_{city}"
    
    # Если город не определен
    if query_types:
        return '+'.join(query_types)
        
    # Если ничего не определено
    return 'other'

def save_to_database(db: PostgresClient, data: List[Dict[str, Any]], date_collected: datetime):
    """Сохранение данных в базу.
    
    Args:
        db: Клиент базы данных
        data: Данные для сохранения
        date_collected: Дата сбора данных
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # Создаем временную таблицу для пакетной вставки
            cur.execute("""
                CREATE TEMP TABLE temp_queries (
                    query TEXT,
                    query_type TEXT,
                    url TEXT,
                    position FLOAT,
                    clicks INTEGER,
                    impressions INTEGER,
                    ctr FLOAT,
                    date_collected DATE
                ) ON COMMIT DROP
            """)
            
            # Подготавливаем данные для вставки
            rows = [
                (
                    row['keys'][0],  # query
                    categorize_query(row['keys'][0]),  # query_type
                    row['keys'][1],  # url
                    row['position'],
                    row['clicks'],
                    row['impressions'],
                    row['ctr'],
                    date_collected.date()
                )
                for row in data
            ]
            
            # Пакетная вставка во временную таблицу
            cur.executemany("""
                INSERT INTO temp_queries 
                (query, query_type, url, position, clicks, impressions, ctr, date_collected)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, rows)
            
            # Вставка из временной таблицы в основную
            cur.execute("""
                INSERT INTO search_queries 
                (query, query_type, url, position, clicks, impressions, ctr, date_collected)
                SELECT query, query_type, url, position, clicks, impressions, ctr, date_collected
                FROM temp_queries
            """)
            
            conn.commit()

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
        
        # Получаем данные за два 30-дневных периода
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        prev_end_date = start_date
        prev_start_date = prev_end_date - timedelta(days=30)
        
        # Получаем данные за текущий период
        logger.info(f"Fetching data for current period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        current_data = fetch_search_data(service, site_url, start_date, end_date)
        
        # Получаем данные за предыдущий период
        logger.info(f"Fetching data for previous period: {prev_start_date.strftime('%Y-%m-%d')} to {prev_end_date.strftime('%Y-%m-%d')}")
        previous_data = fetch_search_data(service, site_url, prev_start_date, prev_end_date)
        
        if current_data:
            # Сохраняем текущие данные
            db = PostgresClient()
            save_to_database(db, current_data, end_date)
            logger.info(f"Successfully saved {len(current_data)} current period search queries")
            
            # Сохраняем предыдущие данные
            if previous_data:
                save_to_database(db, previous_data, prev_end_date)
                logger.info(f"Successfully saved {len(previous_data)} previous period search queries")
            
            # Выводим топ-10 запросов для проверки
            logger.info("\nTop 10 queries by clicks (current period):")
            for i, row in enumerate(current_data[:10], 1):
                logger.info(f"{i}. Query: {row['keys'][0]}")
                logger.info(f"   URL: {row['keys'][1]}")
                logger.info(f"   Clicks: {row['clicks']}, Position: {row['position']:.1f}")
        else:
            logger.warning("No data received from Search Console")
            
    except Exception as e:
        logger.error(f"Error fetching search data: {e}")
        raise

if __name__ == "__main__":
    main()
