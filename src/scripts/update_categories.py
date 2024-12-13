"""Скрипт для обновления категорий запросов в базе данных."""
import os
import sys
from typing import Dict, List

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.utils.logger import setup_logger
from fetch_search_data import categorize_query

logger = setup_logger(__name__)

def update_query_categories(db: PostgresClient):
    """Обновление категорий запросов в базе данных."""
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # Получаем все уникальные запросы
            cur.execute("SELECT DISTINCT query FROM search_queries")
            queries = [row[0] for row in cur.fetchall()]
            
            # Обновляем категории для каждого запроса
            for query in queries:
                new_category = categorize_query(query)
                cur.execute("""
                    UPDATE search_queries 
                    SET query_type = %s 
                    WHERE query = %s
                """, (new_category, query))
                logger.info(f"Обновлена категория для запроса '{query}': {new_category}")
            
            conn.commit()
            logger.info(f"Всего обновлено запросов: {len(queries)}")

def main():
    """Main function."""
    try:
        db = PostgresClient()
        update_query_categories(db)
    except Exception as e:
        logger.error(f"Ошибка при обновлении категорий: {e}")
        raise

if __name__ == "__main__":
    main()
