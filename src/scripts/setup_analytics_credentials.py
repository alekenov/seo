"""Скрипт для добавления учетных данных Google Analytics в Supabase."""
import json
import os
import sys

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Основная функция."""
    try:
        # Загружаем JSON файл с учетными данными
        credentials_file = os.path.join(project_root, 'config', 'credentials.json')
        logger.info(f"Загружаем учетные данные из {credentials_file}")
        
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
            
        # Создаем менеджер учетных данных
        credentials_manager = CredentialsManager()
        
        # Проверяем наличие всех необходимых полей
        required_fields = [
            'type',
            'project_id',
            'private_key_id',
            'private_key',
            'client_email',
            'client_id',
            'auth_uri',
            'token_uri',
            'auth_provider_x509_cert_url',
            'client_x509_cert_url'
        ]
        
        missing_fields = [field for field in required_fields if field not in creds]
        if missing_fields:
            raise ValueError(f"В файле credentials.json отсутствуют поля: {', '.join(missing_fields)}")
            
        # Сохраняем каждое значение отдельно
        for key in required_fields:
            try:
                credentials_manager.save_credential('analytics', key, creds[key])
                logger.info(f"Добавлены учетные данные: analytics.{key}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении {key}: {e}")
                raise
            
        # Добавляем property_id (его нужно будет указать вручную)
        logger.info("\nВНИМАНИЕ: Не забудьте добавить property_id для GA4!")
        logger.info("Пример:")
        logger.info("credentials_manager.save_credential('analytics', 'property_id', 'ваш_property_id')")
        
    except FileNotFoundError:
        logger.error(f"Файл {credentials_file} не найден")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка при разборе JSON файла: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ошибка при добавлении учетных данных: {e}")
        sys.exit(1)
        
    logger.info("Учетные данные успешно добавлены в Supabase!")

if __name__ == "__main__":
    main()
