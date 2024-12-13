"""Скрипт для просмотра отслеживаемых запросов."""
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_tracked_queries(db: PostgresClient):
    """Получение списка отслеживаемых запросов."""
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # Получаем типы запросов
            cur.execute("SELECT DISTINCT query_type FROM search_queries WHERE query_type IS NOT NULL")
            query_types = [r[0] for r in cur.fetchall()]
            logger.info(f"Типы запросов: {query_types}")
            
            # Получаем топ запросов по позициям для каждого типа
            for qtype in query_types:
                logger.info(f"\nТоп-10 запросов типа '{qtype}' по позициям:")
                logger.info("-" * 80)
                
                cur.execute("""
                    SELECT 
                        query,
                        position,
                        clicks,
                        impressions,
                        date_collected
                    FROM search_queries 
                    WHERE query_type = %s
                    ORDER BY position ASC
                    LIMIT 10
                """, (qtype,))
                
                for row in cur.fetchall():
                    query, position, clicks, impressions, date = row
                    logger.info(
                        f"Запрос: {query}\n"
                        f"Позиция: {position:.1f}, "
                        f"Клики: {clicks}, "
                        f"Показы: {impressions}, "
                        f"Дата: {date}"
                    )

def main():
    """Основная функция."""
    db = PostgresClient()
    get_tracked_queries(db)

if __name__ == "__main__":
    main()
