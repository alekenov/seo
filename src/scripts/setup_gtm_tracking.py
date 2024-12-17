"""
Скрипт для настройки базового отслеживания в GTM
"""
import logging
import os
import sys
from pathlib import Path
from src.services.gtm_service import GTMService
from src.services.credentials_manager import CredentialsManager

# Добавляем корневую директорию в PYTHONPATH
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Получаем GA4 credentials из базы данных
        credentials_manager = CredentialsManager()
        ga4_credentials = credentials_manager.get_credentials('ga4')
        if not ga4_credentials:
            logger.error("Не удалось получить GA4 credentials из базы данных")
            return

        measurement_id = ga4_credentials.get('measurement_id')
        if not measurement_id:
            logger.error("Measurement ID не найден в GA4 credentials")
            return

        logger.info(f"Используем GA4 Measurement ID: {measurement_id}")

        # Инициализируем GTM сервис
        logger.info("\nИнициализация GTM сервиса...")
        gtm_service = GTMService(credentials_manager)
        
        # Проверяем рабочие области
        logger.info("\nПроверка рабочих областей GTM...")
        workspaces = gtm_service.list_workspaces()
        
        if not workspaces:
            logger.error("Не найдены рабочие области в GTM контейнере")
            return
        
        # Проверяем разрешения
        logger.info("\nПроверка разрешений GTM API...")
        gtm_service.check_permissions()
        
        # Настраиваем базовое отслеживание
        logger.info("\nНастройка базового отслеживания...")
        gtm_service.setup_basic_tracking(measurement_id)
        
        logger.info("\nGTM настройка завершена успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке GTM: {str(e)}")
        raise

if __name__ == "__main__":
    main()
