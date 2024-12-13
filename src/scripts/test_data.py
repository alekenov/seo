"""Скрипт для получения тестовых данных из Supabase."""

from datetime import datetime, timedelta
from src.database.supabase_client import SupabaseClient


def main():
    """Основная функция."""
    try:
        # Создаем клиент
        db = SupabaseClient()
        
        # Получаем данные за последние 7 дней
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        print(f"Получаем данные с {start_date} по {end_date}...")
        
        metrics = db.get_metrics_by_date_range(
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"\nНайдено {len(metrics)} записей:")
        for metric in metrics[:5]:  # Показываем первые 5 записей
            print(f"\nЗапрос: {metric['query']}")
            print(f"Дата: {metric['date']}")
            print(f"Клики: {metric['clicks']}")
            print(f"Показы: {metric['impressions']}")
            print(f"Позиция: {metric['position']:.1f}")
            print(f"CTR: {metric['ctr']:.2%}")
            if metric.get('url'):
                print(f"URL: {metric['url']}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == '__main__':
    main()
