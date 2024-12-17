"""
Скрипт для применения миграции
"""
import os
import sys
import argparse

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Применение миграции."""
    try:
        # Парсим аргументы
        parser = argparse.ArgumentParser(description='Apply database migration')
        parser.add_argument('migration_file', help='Migration file name (e.g., update_gsc_refresh_token.sql)')
        args = parser.parse_args()
        
        # Читаем SQL файл
        migration_path = os.path.join(
            project_root, 
            'src', 
            'database', 
            'migrations',
            args.migration_file
        )
        
        if not os.path.exists(migration_path):
            logger.error(f"Migration file not found: {migration_path}")
            return
        
        with open(migration_path, 'r') as f:
            sql = f.read()
        
        # Применяем миграцию
        db = PostgresClient()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()
        
        logger.info(f"Migration {args.migration_file} applied successfully")
        
    except Exception as e:
        logger.error(f"Error applying migration: {e}")
        raise

if __name__ == "__main__":
    main()
