"""Скрипт для обновления refresh_token в базе данных."""
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
        
        # Новый refresh_token
        refresh_token = "1//0c-_Fc9T8QJvfCgYIARAAGAwSNwF-L9IrpuX_Ub-c5jS12Ct7Ftj8PTXQoq_xgLERsak6GWGPOaN8q4ijR_yMDkFBXL5-XZNOqZs"
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Обновляем существующую запись
                cur.execute(
                    """
                    UPDATE credentials 
                    SET key_value = %s 
                    WHERE service_name = 'gsc' AND key_name = 'refresh_token'
                    """,
                    (refresh_token,)
                )
                
                conn.commit()
                
        logger.info("Refresh token updated successfully")
        
    except Exception as e:
        logger.error(f"Error updating refresh token: {str(e)}")

if __name__ == "__main__":
    main()
