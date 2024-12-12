import os
import sys
import psycopg2
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple
from psycopg2.extras import execute_batch

# Добавляем корневую директорию проекта в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

def connect_to_db():
    """Подключение к базе данных"""
    return psycopg2.connect(
        dbname="postgres",
        user="postgres.jvfjxlpplbyrafasobzl",
        password="fogdif-7voHxi-ryfqug",
        host="aws-0-eu-central-1.pooler.supabase.com",
        port="6543"
    )

class QueryGenerator:
    """Генератор поисковых запросов с категоризацией"""
    
    def __init__(self):
        # Базовые шаблоны запросов по категориям
        self.templates = {
            'delivery': [  # доставка цветов
                "доставка цветов {}",
                "доставка цветов в {}",
                "заказать доставку цветов {}"
            ],
            'flowers': [  # цветы
                "купить цветы {}",
                "цветы {}",
                "цветы в {}"
            ],
            'bouquets': [  # букеты
                "букет купить {}",
                "букет роз {}",
                "свадебный букет {}"
            ],
            'gifts': [  # подарки
                "цветы в подарок {}",
                "подарочный букет {}"
            ],
            'other': [  # другое
                "недорогие цветы {}",
                "цветы недорого {}"
            ]
        }
        
    def generate_for_city(self, city: str) -> List[Tuple[str, str]]:
        """Генерирует все варианты запросов для города с категориями"""
        queries = []
        for category, templates in self.templates.items():
            for template in templates:
                query = template.format(city)
                queries.append((query, category))
        return queries

def add_cities(cursor) -> Dict[str, int]:
    """Добавление городов"""
    cities = [
        ("Алматы", "Almaty"),
        ("Астана", "Astana"),
        ("Шымкент", "Shymkent")
    ]
    
    city_ids = {}
    for city_name, city_name_en in cities:
        print(f"Добавляем город: {city_name}")
        cursor.execute("""
            INSERT INTO cities (name, name_en, created_at, updated_at)
            VALUES (%s, %s, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE 
            SET name = EXCLUDED.name, name_en = EXCLUDED.name_en
            RETURNING id
        """, (city_name, city_name_en))
        city_ids[city_name] = cursor.fetchone()[0]
    
    return city_ids

def add_search_queries(cursor, city_ids) -> List[int]:
    """Добавление поисковых запросов"""
    query_ids = []
    generator = QueryGenerator()
    
    for city, city_id in city_ids.items():
        queries = generator.generate_for_city(city)
        for query, category in queries:
            print(f"Добавляем запрос [{category}]: {query}")
            cursor.execute("""
                INSERT INTO search_queries (query, city_id, query_type, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
                ON CONFLICT (query, date_collected) DO UPDATE 
                SET city_id = EXCLUDED.city_id,
                    query_type = EXCLUDED.query_type
                RETURNING id
            """, (query, city_id, category))
            query_ids.append(cursor.fetchone()[0])
    
    return query_ids

def generate_metrics(base_position: float) -> Tuple[int, int, float, float]:
    """Генерация метрик на основе позиции"""
    position_factor = max(0.1, (21 - base_position) / 20)
    clicks = int(random.randint(5, 30) * position_factor)
    impressions = int(clicks * random.randint(20, 40))
    ctr = clicks / impressions if impressions > 0 else 0
    return clicks, impressions, base_position, ctr

def add_daily_metrics(cursor, query_ids: List[int], days: int = 60):
    """Добавление ежедневных метрик пакетами"""
    end_date = datetime.now()
    batch_size = 100
    metrics_data = []
    
    # Генерируем базовые позиции для каждого запроса
    query_positions = {qid: random.uniform(1, 10) for qid in query_ids}
    
    print(f"Генерируем метрики за {days} дней...")
    for days_ago in range(days):
        date = end_date - timedelta(days=days_ago)
        
        for query_id in query_ids:
            # Генерируем позицию с небольшим случайным изменением
            base_pos = query_positions[query_id]
            position = max(1.0, min(20.0, base_pos + random.uniform(-1.5, 1.5)))
            clicks, impressions, _, ctr = generate_metrics(position)
            
            metrics_data.append((
                date.date(), query_id, clicks, impressions,
                position, ctr, datetime.now(), datetime.now()
            ))
            
            # Если накопили достаточно данных, отправляем пакет
            if len(metrics_data) >= batch_size:
                print(f"Добавляем пакет метрик... (дата: {date.date()})")
                execute_batch(cursor, """
                    INSERT INTO daily_metrics 
                    (date, query_id, clicks, impressions, position, ctr, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (date) DO UPDATE 
                    SET clicks = EXCLUDED.clicks,
                        impressions = EXCLUDED.impressions,
                        position = EXCLUDED.position,
                        ctr = EXCLUDED.ctr
                """, metrics_data)
                metrics_data = []
    
    # Добавляем оставшиеся данные
    if metrics_data:
        print("Добавляем последний пакет метрик...")
        execute_batch(cursor, """
            INSERT INTO daily_metrics 
            (date, query_id, clicks, impressions, position, ctr, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date) DO UPDATE 
            SET clicks = EXCLUDED.clicks,
                impressions = EXCLUDED.impressions,
                position = EXCLUDED.position,
                ctr = EXCLUDED.ctr
        """, metrics_data)

def main():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        print("Добавляем города...")
        city_ids = add_cities(cursor)
        conn.commit()
        
        print("\nДобавляем поисковые запросы...")
        query_ids = add_search_queries(cursor, city_ids)
        conn.commit()
        
        print(f"\nДобавляем метрики за последние 60 дней...")
        add_daily_metrics(cursor, query_ids, days=60)
        conn.commit()
        
        print("\nГотово!")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
