"""Скрипт для настройки Google Ads API."""
import os
import sys
import shutil
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def setup_service_account():
    """Настройка сервисного аккаунта."""
    try:
        # Путь к исходному JSON файлу
        source_json = os.path.join(project_root, 'thinking-field-415009-ddb12ae41a92.json')
        
        # Создаем директорию config если её нет
        config_dir = os.path.join(project_root, 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        # Путь куда копируем JSON файл
        target_json = os.path.join(config_dir, 'thinking-field-415009-ddb12ae41a92.json')
        
        # Копируем файл в config директорию
        shutil.copy2(source_json, target_json)
        logger.info(f"JSON файл сервисного аккаунта скопирован в {target_json}")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при настройке сервисного аккаунта: {str(e)}")
        return False

def apply_migration():
    """Применение миграции для добавления учетных данных Google Ads."""
    try:
        db = PostgresClient()
        migration_path = Path(project_root) / "src" / "database" / "migrations" / "add_google_ads_credentials.sql"
        
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
            
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(migration_sql)
                conn.commit()
                
        logger.info("Миграция успешно применена")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при применении миграции: {str(e)}")
        return False

def main():
    """Основная функция."""
    try:
        # Настраиваем сервисный аккаунт
        if not setup_service_account():
            logger.error("Не удалось настроить сервисный аккаунт")
            return
            
        # Применяем миграцию
        if not apply_migration():
            logger.error("Не удалось применить миграцию")
            return
            
        # Проверяем, что учетные данные успешно сохранены
        creds = CredentialsManager()
        
        logger.info("\nДоступные учетные данные Google Ads:")
        service_creds = creds.get_service_credentials('google_ads')
        for key, value in service_creds.items():
            # Маскируем значение, показывая только первые и последние 4 символа
            masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '****'
            logger.info(f"- {key}: {masked_value}")
                
    except Exception as e:
        logger.error(f"Ошибка при настройке: {str(e)}")

if __name__ == "__main__":
    main()
