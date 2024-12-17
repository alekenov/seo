"""
Скрипт для проверки работы с Google Tag Manager API
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
        logger.info("Инициализация GTM сервиса")
        gtm = GTMService()
        
        # Получаем и выводим информацию о тегах
        logger.info("Получение списка тегов")
        tags = gtm.get_tags()
        logger.info(f"Найдено тегов: {len(tags)}")
        for tag in tags:
            logger.info(f"Тег: {tag.get('name')} (Тип: {tag.get('type')})")
        
        # Получаем и выводим информацию о триггерах
        logger.info("\nПолучение списка триггеров")
        triggers = gtm.get_triggers()
        logger.info(f"Найдено триггеров: {len(triggers)}")
        for trigger in triggers:
            logger.info(f"Триггер: {trigger.get('name')} (Тип: {trigger.get('type')})")
        
        # Получаем и выводим информацию о переменных
        logger.info("\nПолучение списка переменных")
        variables = gtm.get_variables()
        logger.info(f"Найдено переменных: {len(variables)}")
        for variable in variables:
            logger.info(f"Переменная: {variable.get('name')} (Тип: {variable.get('type')})")
        
        # Анализируем контейнер
        logger.info("\nАнализ контейнера GTM")
        analysis = gtm.analyze_container()
        
        logger.info("\nРезультаты анализа:")
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
        
    except Exception as e:
        logger.error(f"Ошибка при работе с GTM API: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
