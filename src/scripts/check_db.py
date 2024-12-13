"""Скрипт для проверки структуры базы данных."""
import os
import sys
from datetime import datetime, timedelta

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def check_db_structure():
    """Проверка структуры базы данных."""
    db = PostgresClient()
    
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # Проверяем структуру таблицы
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'search_queries';
            """)
            
            logger.info("\nСтруктура таблицы search_queries:")
            logger.info("-" * 50)
            for col in cur.fetchall():
                logger.info(f"Колонка: {col[0]}, Тип: {col[1]}")
            
            # Проверяем данные
            cur.execute("""
                SELECT query_type, COUNT(*) 
                FROM search_queries 
                GROUP BY query_type;
            """)
            
            logger.info("\nТипы запросов в базе:")
            logger.info("-" * 50)
            for row in cur.fetchall():
                logger.info(f"Тип: {row[0]}, Количество: {row[1]}")
            
            # Проверяем последние записи
            cur.execute("""
                SELECT query, query_type, clicks, impressions, position, date_collected
                FROM search_queries
                ORDER BY date_collected DESC
                LIMIT 5;
            """)
            
            logger.info("\nПоследние 5 записей:")
            logger.info("-" * 50)
            for row in cur.fetchall():
                logger.info(f"Запрос: {row[0]}")
                logger.info(f"Тип: {row[1]}")
                logger.info(f"Клики: {row[2]}")
                logger.info(f"Показы: {row[3]}")
                logger.info(f"Позиция: {row[4]}")
                logger.info(f"Дата: {row[5]}")
                logger.info("-" * 30)

if __name__ == "__main__":
    check_db_structure()
