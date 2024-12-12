import os
import sys
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from collections import Counter

# Добавляем корневую директорию проекта в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.data_aggregator import DataAggregator

def analyze_query_words(cursor):
    """Анализ слов в поисковых запросах"""
    cursor.execute("""
        SELECT query, SUM(dm.impressions) as total_impressions
        FROM search_queries sq
        JOIN daily_metrics dm ON sq.id = dm.query_id
        GROUP BY query
        ORDER BY total_impressions DESC
    """)
    queries = cursor.fetchall()
    
    # Собираем все слова
    words = []
    for q in queries:
        words.extend(q['query'].lower().split())
    
    # Подсчитываем частоту слов
    word_freq = Counter(words)
    
    print("\nТоп-10 самых частых слов в запросах:")
    for word, count in word_freq.most_common(10):
        print(f"'{word}': {count} раз")

def check_data():
    """Проверка данных в базе"""
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres.jvfjxlpplbyrafasobzl",
        password="fogdif-7voHxi-ryfqug",
        host="aws-0-eu-central-1.pooler.supabase.com",
        port="6543"
    )
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Проверяем данные в таблице daily_metrics
        cursor.execute("""
            SELECT 
                MIN(date) as min_date,
                MAX(date) as max_date,
                COUNT(*) as total_records,
                COUNT(DISTINCT query_id) as unique_queries
            FROM daily_metrics
        """)
        metrics_info = cursor.fetchone()
        
        print("\nИнформация о данных в daily_metrics:")
        print(f"Период данных: с {metrics_info['min_date']} по {metrics_info['max_date']}")
        print(f"Всего записей: {metrics_info['total_records']}")
        print(f"Уникальных запросов: {metrics_info['unique_queries']}")
        
        # Проверяем топ-5 запросов по показам за последние 90 дней
        cursor.execute("""
            SELECT 
                sq.query,
                dm.query_id,
                COUNT(*) as days,
                AVG(dm.position) as avg_position,
                SUM(dm.clicks) as total_clicks,
                SUM(dm.impressions) as total_impressions,
                AVG(dm.ctr) as avg_ctr
            FROM daily_metrics dm
            JOIN search_queries sq ON dm.query_id = sq.id
            WHERE dm.date >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY sq.query, dm.query_id
            ORDER BY total_impressions DESC
            LIMIT 5
        """)
        top_queries = cursor.fetchall()
        
        print("\nТоп-5 запросов по показам за последние 90 дней:")
        for q in top_queries:
            print(f"\nЗапрос: {q['query']} (слов: {len(q['query'].split())})")
            print(f"ID: {q['query_id']}")
            print(f"Дней в выборке: {q['days']}")
            print(f"Средняя позиция: {q['avg_position']:.2f}")
            print(f"Всего кликов: {q['total_clicks']}")
            print(f"Всего показов: {q['total_impressions']}")
            print(f"Средний CTR: {(q['avg_ctr'] * 100):.2f}%")
        
        # Анализируем слова в запросах
        analyze_query_words(cursor)
        
        return top_queries[0]['query_id'] if top_queries else None
        
    finally:
        cursor.close()
        conn.close()

def main():
    # Проверяем данные и получаем ID самого популярного запроса
    print("Проверяем данные в базе...")
    top_query_id = check_data()
    
    if not top_query_id:
        print("Данные в базе не найдены!")
        return
    
    # Создаем экземпляр агрегатора
    aggregator = DataAggregator()
    
    # Тестируем агрегацию за последние 90 дней
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    print("\nНачинаем агрегацию данных...")
    aggregator.aggregate_daily_to_weekly(start_date, end_date)
    print("Агрегация завершена")
    
    # Рассчитываем метрики для самого популярного запроса
    print(f"\nРассчитываем средние показатели для top query_id={top_query_id}")
    metrics = aggregator.calculate_average_metrics(top_query_id, days=90)
    print("Результаты за 90 дней:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.2f}")

if __name__ == "__main__":
    main()
