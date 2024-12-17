"""
Скрипт для настройки отслеживания электронной коммерции в GTM
"""
import os
import sys
import logging

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.services.gtm_service import GTMService
from src.database.db import SupabaseDB
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)

def main():
    """
    Основная функция для настройки e-commerce в GTM
    """
    try:
        # Инициализируем сервисы
        db = SupabaseDB()
        gtm = GTMService(db)
        
        # Тестируем создание одного триггера
        trigger = gtm.create_ecommerce_trigger('customEvent', 'view_item')
        logger.info(f"Триггер создан: {trigger}")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке e-commerce в GTM: {str(e)}")
        raise

if __name__ == "__main__":
    setup_logger(__name__)
    main()
