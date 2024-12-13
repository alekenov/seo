"""Скрипт для получения заказов из CRM API."""
import requests
import pandas as pd
from datetime import datetime, timedelta
import psycopg2
from src.config.supabase_config import DATABASE_URL
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_orders():
    """Получение заказов из CRM API."""
    # API параметры
    url = "https://cvety.kz/api/order/order-list"
    token = "ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144"
    
    # Параметры запроса
    params = {
        "access_token": token,  # Исправили название параметра
        "limit": 10,
        "status_id": None  # Все статусы
    }
    
    try:
        logger.info(f"Отправляем запрос к API: {url}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Получен ответ от API: {data}")
        
        orders = data.get('data', {}).get('orders', [])
        logger.info(f"Найдено заказов: {len(orders)}")
        
        if not orders:
            logger.warning("Заказы не найдены в ответе API")
            return
        
        # Подключаемся к базе данных
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Создаем таблицу если не существует
        with open('src/database/migrations/create_crm_orders_table.sql', 'r') as f:
            cur.execute(f.read())
            
        # Обрабатываем каждый заказ
        for order in orders:
            logger.info(f"Обрабатываем заказ: {order}")
            
            # Готовим данные для вставки
            order_data = (
                int(order.get('id', 0)),
                float(order.get('price', 0)),
                order.get('status_word', ''),
                bool(order.get('canceled', False)),
                order.get('currency', 'KZT'),
                float(order.get('delivery_price', 0)) if order.get('delivery_price') else None
            )
            
            logger.info(f"Подготовленные данные: {order_data}")
            
            # Вставляем или обновляем заказ
            cur.execute("""
                INSERT INTO crm_orders (
                    order_id, order_sum, status, is_cancelled, currency, delivery_cost
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_id) DO UPDATE SET
                    order_sum = EXCLUDED.order_sum,
                    status = EXCLUDED.status,
                    is_cancelled = EXCLUDED.is_cancelled,
                    currency = EXCLUDED.currency,
                    delivery_cost = EXCLUDED.delivery_cost,
                    updated_at = CURRENT_TIMESTAMP
            """, order_data)
            
        # Сохраняем изменения
        conn.commit()
        logger.info("Данные успешно сохранены в базу")
        
        # Получаем статистику по статусам
        cur.execute("SELECT status, COUNT(*) as count FROM crm_orders GROUP BY status")
        status_counts = pd.DataFrame(cur.fetchall(), columns=['Статус', 'count'])
        logger.info("\nСтатистика по статусам:")
        logger.info(status_counts.to_string())
        
        # Получаем последние 10 заказов
        cur.execute("""
            SELECT order_id as ID, order_sum as Сумма, status as Статус,
                   is_cancelled as Отменен, currency as Валюта,
                   delivery_cost as "Стоимость доставки"
            FROM crm_orders
            ORDER BY created_at DESC
            LIMIT 10
        """)
        recent_orders = pd.DataFrame(cur.fetchall(), columns=[
            'ID', 'Сумма', 'Статус', 'Отменен', 'Валюта', 'Стоимость доставки'
        ])
        logger.info("\nПоследние заказы:")
        logger.info(recent_orders.to_string())
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к API: {e}")
        if hasattr(e.response, 'text'):
            logger.error(f"Ответ сервера: {e.response.text}")
    except psycopg2.Error as e:
        logger.error(f"Ошибка базы данных: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    get_orders()
