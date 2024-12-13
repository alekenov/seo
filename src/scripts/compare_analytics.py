"""
Сравнение данных из разных источников аналитики
"""
import os
import sys
from datetime import datetime
import pandas as pd

# Добавляем путь к src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.yandex_metrika import YandexMetrika
from services.google_analytics import GoogleAnalytics

def format_number(num):
    """Форматирование чисел для вывода"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    if num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def main():
    # Инициализируем клиентов
    ym = YandexMetrika()
    ga = GoogleAnalytics('YOUR_GA4_PROPERTY_ID')  # Замените на ваш ID свойства GA4
    
    print("\n=== Сравнение данных аналитики ===")
    print("-" * 50)
    
    # Получаем данные из Яндекс.Метрики
    ym_data = ym.get_today_metrics()
    
    # Получаем данные из Google Analytics
    ga_data = ga.get_today_metrics()
    
    # Создаем DataFrame для сравнения
    sources = set()
    for source in ym_data['sources']:
        sources.add(source['source'])
    for source in ga_data['sources']:
        sources.add(source['source'])
        
    comparison = []
    for source in sources:
        ym_source = next((s for s in ym_data['sources'] if s['source'] == source), None)
        ga_source = next((s for s in ga_data['sources'] if s['source'] == source), None)
        
        row = {
            'source': source,
            'ym_visits': ym_source['visits'] if ym_source else 0,
            'ga_visits': ga_source['visits'] if ga_source else 0,
            'ym_orders': ym_source['orders'] if ym_source else 0,
            'ga_orders': ga_source['orders'] if ga_source else 0,
            'ym_revenue': ym_source['revenue'] if ym_source else 0,
            'ga_revenue': ga_source['revenue'] if ga_source else 0,
        }
        
        # Расчет разницы в процентах
        row['visits_diff'] = ((row['ga_visits'] - row['ym_visits']) / row['ym_visits'] * 100) if row['ym_visits'] > 0 else 0
        row['orders_diff'] = ((row['ga_orders'] - row['ym_orders']) / row['ym_orders'] * 100) if row['ym_orders'] > 0 else 0
        row['revenue_diff'] = ((row['ga_revenue'] - row['ym_revenue']) / row['ym_revenue'] * 100) if row['ym_revenue'] > 0 else 0
        
        comparison.append(row)
        
    df = pd.DataFrame(comparison)
    
    # Выводим результаты
    print(f"\nДанные за {datetime.now().strftime('%Y-%m-%d')}")
    print("\nИсточник трафика:")
    for _, row in df.iterrows():
        print(f"\n{row['source']}:")
        print(f"  Визиты: YM={format_number(row['ym_visits'])} GA={format_number(row['ga_visits'])} ({row['visits_diff']:.1f}%)")
        print(f"  Заказы: YM={format_number(row['ym_orders'])} GA={format_number(row['ga_orders'])} ({row['orders_diff']:.1f}%)")
        print(f"  Выручка: YM={format_number(row['ym_revenue'])} GA={format_number(row['ga_revenue'])} ({row['revenue_diff']:.1f}%)")
        
    # Сохраняем данные в CSV для дальнейшего анализа
    df.to_csv(f'analytics_comparison_{datetime.now().strftime("%Y%m%d")}.csv', index=False)
    print(f"\nДанные сохранены в файл analytics_comparison_{datetime.now().strftime('%Y%m%d')}.csv")

if __name__ == "__main__":
    main()
