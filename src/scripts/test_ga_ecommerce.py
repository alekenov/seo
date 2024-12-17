"""Тестовый скрипт для GA4."""
from datetime import datetime, timedelta
from src.services.google_analytics import GoogleAnalytics

def format_number(num):
    """Форматирование числа для вывода"""
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"

def format_currency(num):
    """Форматирование валюты для вывода"""
    return f"{num:,.2f} KZT"

def format_percent(num):
    """Форматирование процентов для вывода"""
    return f"{num:.2f}%"

def main():
    """Основная функция."""
    # Создаем экземпляр GoogleAnalytics
    ga = GoogleAnalytics()
    
    # Получаем даты для анализа
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print("\n" + "="*50)
    print(f"Анализ данных с {start_date} по {end_date}")
    print("="*50 + "\n")
    
    # 1. Общая статистика продаж
    print("\n1. ОБЩАЯ СТАТИСТИКА ПРОДАЖ")
    print("-"*30)
    
    overview = ga.get_ecommerce_overview(start_date, end_date)
    
    print(f"Общая выручка: {format_currency(overview['total_revenue'])}")
    print(f"Количество заказов: {format_number(overview['transactions'])}")
    print(f"Средний чек: {format_currency(overview['avg_order_value'])}")
    print()
    
    # 2. Статистика по источникам
    print("\n2. ПРОДАЖИ ПО ИСТОЧНИКАМ")
    print("-"*30)
    
    sources = ga.get_sales_by_source(start_date, end_date)
    
    for source in sources:
        print(f"\nИсточник: {source['source']}")
        print(f"Выручка: {format_currency(source['revenue'])}")
        print(f"Заказов: {format_number(source['transactions'])}")
        print(f"Конверсия: {format_percent(source['conversion_rate'])}")
    
    # 3. Статистика по товарам
    print("\n3. ТОП-10 ТОВАРОВ")
    print("-"*30)
    print()
    
    products = ga.get_product_performance(start_date, end_date, limit=10)
    
    for product in products:
        print(f"Товар: {product['name']} ")
        print(f"Выручка: {format_currency(product['revenue'])} KZT")
        print(f"Количество: {format_number(product['quantity'])}")
        print()
    
    # 4. Воронка покупок
    print("\n4. ВОРОНКА ПОКУПОК")
    print("-"*30)
    
    funnel = ga.get_purchase_funnel(start_date, end_date)
    
    print(f"Просмотры страниц: {format_number(funnel['page_views'])}")
    print(f"Добавления в корзину: {format_number(funnel['add_to_carts'])}")
    print(f"Покупки: {format_number(funnel['purchases'])}")
    print(f"Конверсия в корзину: {format_percent(funnel['cart_rate'])}")
    print(f"Конверсия в покупку: {format_percent(funnel['purchase_rate'])}")
    print(f"Конверсия из корзины в покупку: {format_percent(funnel['cart_to_purchase_rate'])}")
    print()

if __name__ == "__main__":
    main()
