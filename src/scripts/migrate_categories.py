"""Скрипт для миграции категорий запросов на новую систему."""
import os
import sys
from datetime import datetime, timedelta

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.utils.logger import setup_logger
from fetch_search_data import categorize_query

logger = setup_logger(__name__)

def migrate_categories():
    """Миграция категорий на новую систему."""
    db = PostgresClient()
    
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # Получаем все уникальные запросы
            cur.execute("""
                SELECT DISTINCT query 
                FROM search_queries 
                WHERE date_collected >= CURRENT_DATE - INTERVAL '30 days';
            """)
            
            queries = cur.fetchall()
            logger.info(f"Найдено {len(queries)} уникальных запросов")
            
            # Обновляем категории
            updated = 0
            for query_row in queries:
                query = query_row[0]
                new_category = categorize_query(query)
                
                cur.execute("""
                    UPDATE search_queries 
                    SET query_type = %s 
                    WHERE query = %s 
                    AND date_collected >= CURRENT_DATE - INTERVAL '30 days';
                """, (new_category, query))
                
                updated += 1
                if updated % 10 == 0:
                    logger.info(f"Обработано {updated} запросов")
            
            conn.commit()
            logger.info(f"\nОбновлено категорий: {updated}")
            
            # Проверяем результаты
            cur.execute("""
                SELECT query_type, COUNT(*) 
                FROM search_queries 
                WHERE date_collected >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY query_type 
                ORDER BY COUNT(*) DESC;
            """)
            
            logger.info("\nНовые категории:")
            logger.info("-" * 50)
            for row in cur.fetchall():
                logger.info(f"Категория: {row[0]}, Количество: {row[1]}")

if __name__ == "__main__":
    migrate_categories()
