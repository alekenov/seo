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
        
        # Получаем список контейнеров
        containers = gtm_service.list_containers()
        logger.info("Список доступных контейнеров:")
        for container in containers:
            logger.info(f"ID: {container['containerId']}, Public ID: {container['publicId']}, Name: {container['name']}")
        
    except Exception as e:
        logger.error(f"Ошибка при проверке GTM контейнера: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
