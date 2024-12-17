import os
import sys
import logging
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.services.gtm_service import GTMService
from src.database.db import SupabaseDB
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    try:
        # Инициализируем сервисы
        db = SupabaseDB()
        gtm_service = GTMService(db)
        
        # Получаем measurement_id из базы данных
        ga4_creds = db.get_credentials('ga4')
        if not ga4_creds:
            raise Exception("Не найдены учетные данные GA4")
        
        measurement_id = ga4_creds['credentials']['measurement_id']
        
        # Удаляем существующие теги и триггеры
        logger.info("Удаляем существующие теги...")
        gtm_service.delete_all_tags()
        logger.info("Удаляем существующие триггеры...")
        gtm_service.delete_all_triggers()
        
        # Создаем тег GA4 Configuration
        logger.info("Создаем тег GA4 Configuration...")
        ga4_config = gtm_service.setup_ga4_tag(measurement_id)
        
        # Создаем теги событий GA4
        logger.info("Создаем теги событий GA4...")
        event_tags = gtm_service.setup_ga4_events(ga4_config['tagId'])
        
        # Публикуем изменения
        logger.info("Публикуем изменения...")
        gtm_service.publish_workspace()
        
        logger.info("GTM контейнер успешно настроен")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке GTM контейнера: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
