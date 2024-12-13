"""Скрипт для проверки данных в БД."""
import os
import sys
from datetime import datetime, timedelta
import psycopg2

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.config.supabase_config import DATABASE_URL
from src.services.gsc_service import GSCService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def check_gsc_data():
    """Проверяем данные в GSC."""
    gsc = GSCService()
    
    # Проверяем данные за 11 декабря 2023
    target_date = datetime(2023, 12, 11).date()
    
    logger.info(f"Проверяем данные за {target_date}")
    
    try:
        response = gsc.get_search_analytics(
            start_date=target_date,
            end_date=target_date,
            dimensions=['page', 'query', 'date']
        )
        
        if response and 'rows' in response:
            logger.info(f"Найдено {len(response['rows'])} строк")
            # Выводим первые 5 строк
            for row in response['rows'][:5]:
                logger.info(f"Страница: {row['keys'][0]}")
                logger.info(f"Запрос: {row['keys'][1]}")
                logger.info(f"Дата: {row['keys'][2]}")
                logger.info(f"Клики: {row['clicks']}")
                logger.info(f"Показы: {row['impressions']}")
                logger.info("---")
        else:
            logger.error("Нет данных в ответе")
            
    except Exception as e:
        logger.error(f"Ошибка при получении данных: {e}")

def check_db_data():
    """Проверяем данные в БД."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # Проверяем данные за 11 декабря 2023
        target_date = datetime(2023, 12, 11).date()
        
        # Получаем статистику по типам запросов
        cur.execute("""
            SELECT query_type, COUNT(*) as count, SUM(clicks) as clicks, SUM(impressions) as impressions
            FROM search_queries_daily
            WHERE date = %s
            GROUP BY query_type
            ORDER BY clicks DESC
        """, (target_date,))
        
        rows = cur.fetchall()
        
        if rows:
            logger.info(f"\nСтатистика по типам запросов за {target_date}:")
            for row in rows:
                logger.info(f"Тип: {row[0]}")
                logger.info(f"Количество запросов: {row[1]}")
                logger.info(f"Клики: {row[2]}")
                logger.info(f"Показы: {row[3]}")
                logger.info("---")
        
        # Получаем статистику по городам
        cur.execute("""
            SELECT city, COUNT(*) as count, SUM(clicks) as clicks, SUM(impressions) as impressions
            FROM search_queries_daily
            WHERE date = %s
            GROUP BY city
            ORDER BY clicks DESC
        """, (target_date,))
        
        rows = cur.fetchall()
        
        if rows:
            logger.info(f"\nСтатистика по городам за {target_date}:")
            for row in rows:
                logger.info(f"Город: {row[0]}")
                logger.info(f"Количество запросов: {row[1]}")
                logger.info(f"Клики: {row[2]}")
                logger.info(f"Показы: {row[3]}")
                logger.info("---")
                
        # Топ-10 запросов
        cur.execute("""
            SELECT query, query_type, city, clicks, impressions, position
            FROM search_queries_daily
            WHERE date = %s
            ORDER BY clicks DESC
            LIMIT 10
        """, (target_date,))
        
        rows = cur.fetchall()
        
        if rows:
            logger.info(f"\nТоп-10 запросов за {target_date}:")
            for row in rows:
                logger.info(f"Запрос: {row[0]}")
                logger.info(f"Тип: {row[1]}")
                logger.info(f"Город: {row[2]}")
                logger.info(f"Клики: {row[3]}")
                logger.info(f"Показы: {row[4]}")
                logger.info(f"Позиция: {row[5]}")
                logger.info("---")
        else:
            logger.info(f"В БД нет данных за {target_date}")
            
    except Exception as e:
        logger.error(f"Ошибка при проверке БД: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    logger.info("Начинаем проверку данных...")
    check_gsc_data()
    check_db_data()
