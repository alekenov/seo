from src.services.yandex_metrika import YandexMetrikaAPI
import pandas as pd
from datetime import datetime, timedelta

def test_metrika_connection():
    """
    Тестирование подключения к Яндекс.Метрике и получение основных отчетов
    """
    # Инициализация клиента
    token = 'y0_AgAAAAAIQVdQAAzyygAAAAEcFYUiAACbs5T2SZBAtbCrBXrF7T-3NHSfVw'
    counter_id = 26416359
    
    try:
        metrika = YandexMetrikaAPI(token, counter_id)
        print("✅ Подключение к API успешно установлено")
        
        # 1. Получение данных по источникам трафика
        print("\n📊 Получаем данные по источникам трафика...")
        traffic_sources = metrika.get_traffic_sources(date1='30daysAgo', date2='today')
        print("\nТоп источники трафика:")
        print(traffic_sources.sort_values('visits', ascending=False).head())
        
        # 2. Получение популярных страниц
        print("\n📑 Получаем данные по популярным страницам...")
        popular_pages = metrika.get_popular_pages(date1='30daysAgo', date2='today', limit=5)
        print("\nТоп-5 популярных страниц:")
        print(popular_pages[['url', 'visits']])
        
        # 3. Получение данных по устройствам
        print("\n📱 Получаем данные по устройствам...")
        devices = metrika.get_devices(date1='30daysAgo', date2='today')
        print("\nСтатистика по устройствам:")
        print(devices)
        
        # 4. Получение поисковых фраз
        print("\n🔍 Получаем данные по поисковым фразам...")
        search_phrases = metrika.get_search_phrases(date1='30daysAgo', date2='today', limit=10)
        print("\nТоп-10 поисковых фраз:")
        print(search_phrases)
        
        # Сохранение отчетов
        print("\n💾 Сохраняем отчеты...")
        
        # Создаем директорию для отчетов если её нет
        import os
        os.makedirs('reports', exist_ok=True)
        
        metrika.save_report(traffic_sources, 'reports/traffic_sources.xlsx')
        metrika.save_report(popular_pages, 'reports/popular_pages.xlsx')
        metrika.save_report(devices, 'reports/devices.xlsx')
        metrika.save_report(search_phrases, 'reports/search_phrases.xlsx')
        
        print("\n✅ Все отчеты успешно сохранены в директории 'reports'")
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")

if __name__ == "__main__":
    test_metrika_connection()
