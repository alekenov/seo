"""Скрипт для добавления refresh_token в базу данных."""
import os
import sys

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Main function."""
    try:
        db = PostgresClient()
        
        # Добавляем refresh_token
        refresh_token = "1//0cFGKHvjQHkTACgYIARAAGAwSNwF-L9IrZOhbGWpGZcXYnPOLHVZeYXYPxIaFbhBUDOLBXGzIaGjvYsLvWQqhCTMRwYNXRdRxOWo"
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Проверяем, существует ли уже такая запись
                cur.execute(
                    """
                    SELECT id FROM credentials 
                    WHERE service_name = 'gsc' AND key_name = 'refresh_token'
                    """
                )
                existing = cur.fetchone()
                
                if existing:
                    # Обновляем существующую запись
                    cur.execute(
                        """
                        UPDATE credentials 
                        SET key_value = %s 
                        WHERE service_name = 'gsc' AND key_name = 'refresh_token'
                        """,
                        (refresh_token,)
                    )
                else:
                    # Добавляем новую запись
                    cur.execute(
                        """
                        INSERT INTO credentials (service_name, key_name, key_value)
                        VALUES ('gsc', 'refresh_token', %s)
                        """,
                        (refresh_token,)
                    )
                
                conn.commit()
                
        logger.info("Refresh token added successfully")
        
    except Exception as e:
        logger.error(f"Error adding refresh token: {str(e)}")

if __name__ == "__main__":
    main()
