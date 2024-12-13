import requests
from datetime import datetime, timedelta

class CvetyCRM:
    """
    Класс для работы с API CRM cvety.kz
    """
    def __init__(self, access_token, base_url="https://cvety.kz/local"):
        self.access_token = access_token
        self.base_url = base_url
        
    def _make_request(self, endpoint, method='GET', params=None, data=None):
        """
        Выполнение запроса к API
        """
        url = f"{self.base_url}{endpoint}"
        
        # Добавляем access_token к параметрам запроса
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        print(f"Запрос к: {url}")  # Для отладки
        print(f"Параметры: {params}")  # Для отладки
        
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_orders(self, limit=20, offset=1, filters=None):
        """
        Получение списка заказов
        """
        params = {
            'limit': limit,
            'offset': offset,
            'filter': filters or []
        }
        return self._make_request('/order/order-list', params=params)
    
    def get_order_details(self, order_id):
        """
        Получение детальной информации по заказу
        """
        params = {
            'orderId': order_id
        }
        return self._make_request('/order/order-id/', params=params)
    
    def get_order_statuses(self):
        """
        Получение списка статусов заказов
        """
        return self._make_request('/order/status-order/')

if __name__ == "__main__":
    # Тестируем подключение
    crm = CvetyCRM('ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144')
    try:
        # Получаем список статусов
        print("\n📋 Статусы заказов:")
        statuses = crm.get_order_statuses()
        print(statuses)
        
        # Получаем заказы
        print("\n📦 Заказы:")
        orders = crm.get_orders()
        print(f"Количество заказов: {len(orders) if isinstance(orders, list) else 'Н/Д'}")
        print("\nПервые несколько заказов:")
        if isinstance(orders, list):
            for order in orders[:5]:
                print(f"\nЗаказ #{order.get('id', 'Н/Д')}:")
                print(f"Статус: {order.get('status', 'Н/Д')}")
                print(f"Сумма: {order.get('total', 'Н/Д')} тг")
    
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
