import sys
import os
from datetime import datetime, timedelta

# Добавляем путь к src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_aggregator import DataAggregator

def test_aggregation():
    """
    Тестирование функций агрегации данных
    """
    aggregator = DataAggregator()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    print("1. Тестирование агрегации daily -> weekly")
    try:
        aggregator.aggregate_daily_to_weekly(start_date, end_date)
        print("✓ Агрегация daily -> weekly успешно выполнена")
    except Exception as e:
        print(f"✗ Ошибка при агрегации daily -> weekly: {str(e)}")

    print("\n2. Тестирование агрегации weekly -> monthly")
    try:
        aggregator.aggregate_weekly_to_monthly(start_date, end_date)
        print("✓ Агрегация weekly -> monthly успешно выполнена")
    except Exception as e:
        print(f"✗ Ошибка при агрегации weekly -> monthly: {str(e)}")

    print("\n3. Тестирование расчета средних показателей")
    try:
        # Берем первый query_id из базы
        aggregator.cursor.execute("SELECT DISTINCT query_id FROM daily_metrics LIMIT 1")
        query_id = aggregator.cursor.fetchone()['query_id']
        metrics = aggregator.calculate_average_metrics(query_id, days=30)
        print(f"✓ Средние показатели для query_id={query_id}:")
        for metric, value in metrics.items():
            print(f"  - {metric}: {value:.2f}")
    except Exception as e:
        print(f"✗ Ошибка при расчете средних показателей: {str(e)}")

    print("\n4. Тестирование определения трендов")
    try:
        trends = aggregator.detect_trends(query_id, days=90)
        print(f"✓ Тренды для query_id={query_id}:")
        for metric, trend_data in trends.items():
            direction = trend_data['direction']
            significance = trend_data['significance']
            r_squared = trend_data['r_squared']
            print(f"  - {metric}: {direction} тренд ({significance}, R²={r_squared:.2f})")
    except Exception as e:
        print(f"✗ Ошибка при определении трендов: {str(e)}")

    print("\n5. Тестирование информации о версиях")
    try:
        version_info = aggregator.get_version_info()
        print("✓ Информация о версиях:")
        print(f"  - Последнее обновление: {version_info['last_update']}")
        print(f"  - Всего запросов: {version_info['total_queries']}")
        print(f"  - Всего записей: {version_info['total_records']}")
    except Exception as e:
        print(f"✗ Ошибка при получении информации о версиях: {str(e)}")

if __name__ == "__main__":
    test_aggregation()
