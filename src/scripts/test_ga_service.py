#!/usr/bin/env python3
"""
Тестирование подключения к Google Analytics
"""
import logging
import os
import sys

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.credentials_manager import CredentialsManager
from src.services.google_analytics import GoogleAnalytics

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Получаем Property ID из credentials
        credentials = CredentialsManager()
        property_id = credentials.get_credential('ga', 'property_id')
        
        print(f"\nПолучены данные из Google Analytics:")
        print(f"Property ID: {property_id}\n")
        
        # Инициализируем сервис GA
        ga = GoogleAnalytics(property_id=property_id)
        
        # Получаем метрики
        metrics = ga.get_today_metrics()
        
        print("Метрики по источникам трафика:")
        print("-" * 50)
        
        for source, data in metrics.items():
            print(f"\nИсточник: {source}")
            print(f"Сессии: {data['sessions']}")
            print(f"Активные пользователи: {data['active_users']}")
            print(f"Вовлеченные сессии: {data['engaged_sessions']}")
            
    except Exception as e:
        logger.error(f"Ошибка при тестировании GA: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
