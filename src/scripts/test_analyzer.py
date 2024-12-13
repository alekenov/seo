"""
Скрипт для тестирования анализатора позиций.
"""
import sys
from pathlib import Path
import os
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import DictCursor

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def test_position_changes():
    """Тестирование функции анализа изменений позиций."""
    # Параметры подключения
    conn_params = {
        'host': 'aws-0-eu-central-1.pooler.supabase.com',
        'port': 6543,
        'database': 'postgres',
        'user': 'postgres.jvfjxlpplbyrafasobzl',
        'password': 'fogdif-7voHxi-ryfqug'
    }
    
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor(cursor_factory=DictCursor)
        
        # Создаем функцию для анализа позиций
        with open('src/database/migrations/create_position_analysis_functions.sql', 'r') as f:
            sql = f.read()
            cur.execute(sql)
        conn.commit()
        
        # Тестируем функцию для разных периодов
        current_date = datetime.now().date()
        periods = [1, 7, 30, 60]
        
        print("\n=== Статистика по периодам ===")
        cur.execute("""
            SELECT * FROM get_position_stats(%s, %s::integer[])
        """, (current_date, periods))
        
        for row in cur.fetchall():
            print(f"\nПериод: {row['period_days']} дней")
            print(f"Средняя позиция: {row['avg_position']:.2f}")
            print(f"Улучшилось запросов: {row['improved_count']}")
            print(f"Ухудшилось запросов: {row['declined_count']}")
            print(f"Всего запросов: {row['total_queries']}")
            print(f"Значимых изменений: {row['significant_changes']}")
        
        # Проверяем изменения за 30 дней
        month_ago = current_date - timedelta(days=30)
        cur.execute("""
            SELECT * FROM get_position_changes(%s, %s, %s)
        """, (month_ago, current_date, 3.0))
        
        results = cur.fetchall()
        
        print("\n=== Топ изменений за 30 дней ===")
        for row in results[:10]:  # Показываем только топ-10
            direction = "⬆️" if row['position_change'] < 0 else "⬇️"
            print(f"\nЗапрос: {row['query']}")
            print(f"URL: {row['url']}")
            print(f"Изменение: {direction} {abs(row['position_change']):.1f} (с {row['old_position']:.1f} на {row['new_position']:.1f})")
            print(f"Изменение показов: {row['impressions_change']:+d}")
            print(f"Изменение кликов: {row['clicks_change']:+d}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_position_changes()
