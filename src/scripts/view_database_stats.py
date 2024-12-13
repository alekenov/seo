"""Скрипт для просмотра статистики базы данных."""
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

def get_database_stats(db: PostgresClient):
    """Получение статистики из базы данных."""
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # Получаем общее количество записей
            cur.execute("SELECT COUNT(*) FROM search_queries")
            total_records = cur.fetchone()[0]
            logger.info(f"Всего записей в базе: {total_records}")
            
            # Получаем диапазон дат
            cur.execute("""
                SELECT 
                    MIN(date_collected),
                    MAX(date_collected)
                FROM search_queries
            """)
            min_date, max_date = cur.fetchone()
            if min_date and max_date:
                logger.info(f"Период данных: с {min_date} по {max_date}")
            
            # Получаем статистику по дням
            cur.execute("""
                SELECT 
                    date_collected,
                    COUNT(*) as records,
                    AVG(position) as avg_position,
                    SUM(clicks) as total_clicks,
                    SUM(impressions) as total_impressions
                FROM search_queries
                GROUP BY date_collected
                ORDER BY date_collected DESC
                LIMIT 10
            """)
            
            logger.info("\nСтатистика по последним 10 дням:")
            logger.info("-" * 80)
            
            for row in cur.fetchall():
                date, records, avg_position, clicks, impressions = row
                logger.info(
                    f"Дата: {date}, "
                    f"Записей: {records}, "
                    f"Средняя позиция: {float(avg_position):.1f}, "
                    f"Кликов: {clicks}, "
                    f"Показов: {impressions}"
                )

def main():
    """Основная функция."""
    db = PostgresClient()
    get_database_stats(db)

if __name__ == "__main__":
    main()
