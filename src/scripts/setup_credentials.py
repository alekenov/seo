"""Скрипт для настройки учетных данных."""
import os
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def apply_migration():
    """Применение миграции для создания таблицы credentials."""
    try:
        db = PostgresClient()
        migration_path = Path(project_root) / "src" / "database" / "migrations" / "create_credentials_table.sql"
        
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
            
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(migration_sql)
                conn.commit()
                
        logger.info("Migration applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error applying migration: {str(e)}")
        return False

def main():
    """Main function."""
    try:
        # Применяем миграцию
        if not apply_migration():
            logger.error("Failed to apply migration")
            return
            
        # Проверяем, что учетные данные успешно сохранены
        creds = CredentialsManager()
        
        # Проверяем доступ к Supabase
        supabase_url = creds.get_credential('supabase', 'url')
        if not supabase_url:
            logger.error("Failed to get Supabase URL from credentials")
            return
            
        logger.info("Credentials setup completed successfully")
        logger.info("\nAvailable credentials:")
        
        # Выводим список доступных учетных данных по сервисам
        for service in ['supabase', 'gsc', 'telegram']:
            service_creds = creds.get_service_credentials(service)
            logger.info(f"\n{service.upper()} credentials:")
            for key, value in service_creds.items():
                # Маскируем значение, показывая только первые и последние 4 символа
                masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '****'
                logger.info(f"- {key}: {masked_value}")
                
    except Exception as e:
        logger.error(f"Error in setup: {str(e)}")

if __name__ == "__main__":
    main()
