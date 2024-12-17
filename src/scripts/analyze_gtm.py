"""
Скрипт для анализа контейнера GTM
"""
import os
import sys
from pathlib import Path

# Добавляем путь к корневой директории проекта
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.services.gtm_service import GTMService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    try:
        # Инициализируем сервис GTM
        logger.info("Инициализация GTM сервиса...")
        gtm = GTMService()
        
        # Анализируем контейнер
        logger.info("\nАнализ контейнера GTM...")
        analysis = gtm.analyze_container()
        
        # Выводим результаты
        logger.info("\nОбщая статистика:")
        logger.info(f"Всего тегов: {analysis['summary']['total_tags']}")
        logger.info(f"Всего триггеров: {analysis['summary']['total_triggers']}")
        logger.info(f"Всего переменных: {analysis['summary']['total_variables']}")
        
        logger.info("\nТеги:")
        logger.info(f"GA4 теги: {analysis['tags']['ga4_tags']}")
        logger.info(f"Event теги: {analysis['tags']['event_tags']}")
        
        logger.info("\nТриггеры:")
        logger.info(f"PageView триггеры: {analysis['triggers']['page_view']}")
        logger.info(f"Event триггеры: {analysis['triggers']['events']}")
        
        logger.info("\nПеременные:")
        logger.info(f"DataLayer переменные: {analysis['variables']['data_layer']}")
        
        # Получаем детальную информацию о тегах
        logger.info("\nДетальная информация о тегах:")
        tags = gtm.get_tags()
        for tag in tags:
            logger.info(f"\nТег: {tag.get('name')}")
            logger.info(f"Тип: {tag.get('type')}")
            logger.info(f"Параметры: {tag.get('parameter', [])}")
        
    except Exception as e:
        logger.error(f"Ошибка при анализе GTM: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
