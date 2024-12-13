"""Скрипт для тестирования подключения к Google Analytics."""
import os
import sys
import json
from datetime import datetime, timedelta

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.services.analytics_service import AnalyticsService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Основная функция."""
    try:
        # Загружаем учетные данные
        credentials_file = os.path.join(project_root, 'config', 'credentials.json')
        with open(credentials_file, 'r') as f:
            credentials = json.load(f)
            
        # ID свойства GA4 (замените на ваш)
        property_id = "YOUR_GA4_PROPERTY_ID"
        
        # Создаем сервис
        analytics = AnalyticsService(credentials, property_id)
        
        # Получаем данные за последние 7 дней
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Запрашиваем основные метрики
        report = analytics.get_report(
            start_date=start_date,
            end_date=end_date,
            metrics=['sessions', 'totalUsers', 'screenPageViews'],
            dimensions=['date']
        )
        
        # Выводим результаты
        logger.info("\nРезультаты за последние 7 дней:")
        for row in report['rows']:
            logger.info(f"Дата: {row['date']}")
            logger.info(f"Сессии: {row['sessions']}")
            logger.info(f"Пользователи: {row['totalUsers']}")
            logger.info(f"Просмотры: {row['screenPageViews']}")
            logger.info("-" * 50)
            
    except FileNotFoundError:
        logger.error(f"Файл {credentials_file} не найден")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка при разборе JSON файла: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ошибка при тестировании GA4: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
