"""Скрипт для получения номеров заказов за сегодня из Яндекс.Метрики."""
import os
import sys
from datetime import datetime

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.services.yandex_metrika import YandexMetrikaAPI
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Основная функция."""
    try:
        # Получаем учетные данные
        token = 'y0_AgAAAAAIQVdQAAzyygAAAAEcFYUiAACbs5T2SZBAtbCrBXrF7T-3NHSfVw'
        counter_id = '92915917'
        
        # Создаем клиент Яндекс.Метрики
        ym = YandexMetrikaAPI(token, counter_id)
        
        # Получаем данные за сегодня
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Запрашиваем данные с номерами заказов
        params = {
            'date1': today,
            'date2': today,
            'metrics': 'ym:s:ecommerce>revenue',  # Доход
            'dimensions': 'ym:s:ecommerce>orderId,ym:s:lastTrafficSource',  # ID заказа и источник
            'sort': 'ym:s:ecommerce>orderId'  # Сортировка по номеру заказа
        }
        
        data = ym._make_request(params)
        
        # Выводим результаты
        logger.info("\n=== Заказы за сегодня (Яндекс.Метрика) ===")
        
        if not data.get('data'):
            logger.info("Заказов за сегодня не найдено")
            return
            
        for row in data['data']:
            order_id = row['dimensions'][0]['name']
            source = row['dimensions'][1]['name']
            revenue = float(row['metrics'][0])
            logger.info(f"Заказ №{order_id} | Источник: {source} | Сумма: ${revenue:,.2f}")
            
    except Exception as e:
        logger.error(f"Ошибка при получении данных из Яндекс.Метрики: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
