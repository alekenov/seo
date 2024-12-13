"""Скрипт для получения номеров заказов за сегодня из Google Analytics."""
import os
import sys
import json
from datetime import datetime

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
        credentials_file = os.path.join(project_root, 'dashbords-373217-ba2bbe59eb47.json')
        with open(credentials_file, 'r') as f:
            credentials = json.load(f)
            
        # ID свойства GA4
        property_id = "properties/252026944"
        
        # Создаем сервис
        analytics = AnalyticsService(credentials, property_id)
        
        # Получаем данные за сегодня
        today = datetime.now()
        
        # Запрашиваем данные с номерами заказов
        report = analytics.get_report(
            start_date=today,
            end_date=today,
            metrics=['totalRevenue'],
            dimensions=['transactionId', 'sessionSource']
        )
        
        # Выводим результаты
        logger.info("\n=== Заказы за сегодня (Google Analytics) ===")
        
        if not report.get('rows'):
            logger.info("Заказов за сегодня не найдено")
            return
            
        for row in report['rows']:
            order_id = row['transactionId']
            source = row['sessionSource']
            revenue = float(row['totalRevenue'])
            logger.info(f"Заказ №{order_id} | Источник: {source} | Сумма: ${revenue:,.2f}")
            
    except Exception as e:
        logger.error(f"Ошибка при получении данных из GA4: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
