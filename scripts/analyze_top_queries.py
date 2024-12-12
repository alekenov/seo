"""
Анализ топ-10 запросов по позициям и CTR
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Добавляем путь к проекту в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.config.supabase_config import DATABASE_URL

def analyze_top_queries():
    # Инициализируем клиент PostgreSQL
    client = PostgresClient()
    
    # Получаем данные за последние 30 дней
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    with client.get_connection() as conn:
        with conn.cursor() as cur:
            # SQL запрос для получения топ-10 небрендовых запросов
            query = """
            WITH top_queries AS (
                SELECT 
                    sq.query,
                    AVG(dm.position) as avg_position,
                    AVG(dm.ctr) as avg_ctr,
                    SUM(dm.clicks) as total_clicks,
                    SUM(dm.impressions) as total_impressions,
                    c.name as city
                FROM search_queries sq
                JOIN daily_metrics dm ON sq.id = dm.query_id
                LEFT JOIN cities c ON sq.city_id = c.id
                WHERE 
                    dm.date BETWEEN %s AND %s
                    AND sq.query NOT ILIKE '%%cvety%%'
                    AND sq.query NOT ILIKE '%%kz%%'
                    AND sq.query NOT ILIKE '%%.kz%%'
                GROUP BY sq.query, c.name
                ORDER BY total_clicks DESC
                LIMIT 10
            )
            SELECT 
                q.query,
                q.avg_position,
                q.avg_ctr,
                q.total_clicks,
                q.total_impressions,
                q.city,
                dm.date,
                dm.position as daily_position,
                dm.ctr as daily_ctr
            FROM top_queries q
            JOIN search_queries sq ON q.query = sq.query
            JOIN daily_metrics dm ON sq.id = dm.query_id
            WHERE dm.date BETWEEN %s AND %s
            ORDER BY q.total_clicks DESC, dm.date ASC;
            """
            
            cur.execute(query, (start_date, end_date, start_date, end_date))
            results = cur.fetchall()
    
    # Группируем данные по запросам
    queries_data = {}
    for row in results:
        query = row[0]
        if query not in queries_data:
            queries_data[query] = {
                'avg_position': row[1],
                'avg_ctr': row[2],
                'total_clicks': row[3],
                'total_impressions': row[4],
                'city': row[5],
                'daily_data': []
            }
        queries_data[query]['daily_data'].append({
            'date': row[6],
            'position': row[7],
            'ctr': row[8]
        })
    
    # Выводим результаты
    print("\nТоп-10 небрендовых запросов за последние 30 дней:")
    print("-" * 80)
    
    for query, data in queries_data.items():
        print(f"\nЗапрос: {query}")
        if data['city']:
            print(f"Город: {data['city']}")
        print(f"Всего кликов: {data['total_clicks']}")
        print(f"Всего показов: {data['total_impressions']}")
        print(f"Средняя позиция: {data['avg_position']:.2f}")
        print(f"Средний CTR: {data['avg_ctr']:.2%}")
        
        if data['daily_data']:
            # Анализируем изменение позиций
            positions = [d['position'] for d in data['daily_data']]
            first_pos = positions[0]
            last_pos = positions[-1]
            pos_change = first_pos - last_pos
            
            print(f"Изменение позиции: {'+' if pos_change > 0 else ''}{pos_change:.2f} "
                  f"(с {first_pos:.2f} до {last_pos:.2f})")
            
            # Анализируем изменение CTR
            ctrs = [d['ctr'] for d in data['daily_data']]
            first_ctr = ctrs[0]
            last_ctr = ctrs[-1]
            ctr_change = (last_ctr - first_ctr) * 100
            
            print(f"Изменение CTR: {'+' if ctr_change > 0 else ''}{ctr_change:.2f}% "
                  f"(с {first_ctr:.2%} до {last_ctr:.2%})")
        else:
            print("Нет данных за указанный период")
        print("-" * 40)

if __name__ == "__main__":
    analyze_top_queries()
