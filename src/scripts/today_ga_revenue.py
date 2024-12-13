"""Скрипт для получения дохода за сегодня из Google Analytics."""
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

def format_currency(amount: float) -> str:
    """Форматирование суммы в доллары."""
    return f"${amount:,.2f}"

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
        
        # Запрашиваем данные
        report = analytics.get_report(
            start_date=today,
            end_date=today,
            metrics=['totalRevenue', 'transactions', 'sessions'],
            dimensions=['sessionSource']
        )
        
        # Суммируем показатели
        total_revenue = 0
        total_transactions = 0
        total_sessions = 0
        
        for row in report['rows']:
            total_revenue += float(row['totalRevenue'])
            total_transactions += int(row['transactions'])
            total_sessions += int(row['sessions'])
        
        # Выводим результаты
        logger.info("\n=== Статистика за сегодня (Google Analytics) ===")
        logger.info(f"Выручка: {format_currency(total_revenue)}")
        logger.info(f"Количество заказов: {total_transactions}")
        logger.info(f"Количество сессий: {total_sessions}")
        
        if total_sessions > 0:
            conversion = (total_transactions / total_sessions) * 100
            logger.info(f"Конверсия: {conversion:.2f}%")
        
        if total_transactions > 0:
            avg_order = total_revenue / total_transactions
            logger.info(f"Средний чек: {format_currency(avg_order)}")
            
    except Exception as e:
        logger.error(f"Ошибка при получении данных из GA4: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
