"""
Скрипт для добавления тестовых поисковых запросов.
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Добавляем корневую директорию проекта в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient

# Тестовые запросы по категориям
TEST_QUERIES = {
    'delivery': [
        'доставка цветов {}',
        'заказать цветы {}',
        'доставка букетов {}',
        'цветы с доставкой {}',
        'доставка роз {}',
    ],
    'bouquets': [
        'букет роз {}',
        'свадебный букет {}',
        'букет пионов {}',
        'букет тюльпанов {}',
        'букет на день рождения {}',
    ],
    'gifts': [
        'подарить цветы {}',
        'подарочный букет {}',
        'цветы в подарок {}',
        'подарок на 8 марта {}',
        'подарок девушке {}',
    ],
    'flowers': [
        'розы {}',
        'пионы {}',
        'тюльпаны {}',
        'хризантемы {}',
        'орхидеи {}',
    ]
}

# Города
CITIES = [
    'Алматы',
    'Астана',
    'Шымкент',
    'Караганда',
    'Костанай',
    'Павлодар',
    'Актобе',
    'Тараз',
    'Семей'
]

def generate_metrics(base_position, trend='stable', volatility='low'):
    """
    Генерация метрик для запроса.
    
    Args:
        base_position: Базовая позиция
        trend: Тренд (up, down, stable)
        volatility: Волатильность (low, medium, high)
    """
    if volatility == 'low':
        variance = 0.5
    elif volatility == 'medium':
        variance = 1.0
    else:
        variance = 2.0
        
    if trend == 'up':
        position_change = -0.1  # Улучшение позиции
    elif trend == 'down':
        position_change = 0.1   # Ухудшение позиции
    else:
        position_change = 0     # Стабильная позиция
        
    position = max(1, min(100, base_position + random.uniform(-variance, variance) + position_change))
    impressions = int(max(10, (100 - position) * random.uniform(5, 15)))
    ctr = max(0.01, min(1.0, (100 - position) * 0.002 * random.uniform(0.8, 1.2)))
    clicks = int(impressions * ctr)
    
    return position, impressions, ctr, clicks

def add_test_data():
    """Добавление тестовых данных."""
    db = PostgresClient()
    
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # Получаем или создаем города
            city_ids = {}
            for city in CITIES:
                cur.execute("""
                    INSERT INTO cities (name, created_at, updated_at)
                    VALUES (%s, NOW(), NOW())
                    ON CONFLICT (name) DO UPDATE SET updated_at = NOW()
                    RETURNING id
                """, (city,))
                city_ids[city] = cur.fetchone()[0]
            
            # Генерируем данные за последние 30 дней
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            current_date = start_date
            
            while current_date <= end_date:
                print(f"\nГенерируем данные для {current_date}")
                
                # Для каждой категории
                for category, queries in TEST_QUERIES.items():
                    # Для каждого шаблона запроса
                    for query_template in queries:
                        # Для каждого города
                        for city in CITIES:
                            query = query_template.format(city)
                            
                            # Генерируем базовую позицию для запроса (1-20)
                            base_position = random.uniform(1, 20)
                            
                            # Определяем тренд и волатильность
                            trend = random.choice(['up', 'down', 'stable'])
                            volatility = random.choice(['low', 'medium', 'high'])
                            
                            # Генерируем метрики
                            position, impressions, ctr, clicks = generate_metrics(
                                base_position, trend, volatility
                            )
                            
                            # Сохраняем запрос
                            cur.execute("""
                                INSERT INTO search_queries 
                                (query, city_id, query_type, clicks, impressions, ctr, position, 
                                 created_at, updated_at, date_collected)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT ON CONSTRAINT search_queries_unique
                                DO UPDATE SET
                                    clicks = EXCLUDED.clicks,
                                    impressions = EXCLUDED.impressions,
                                    ctr = EXCLUDED.ctr,
                                    position = EXCLUDED.position,
                                    updated_at = EXCLUDED.updated_at
                                RETURNING id
                            """, (
                                query,
                                city_ids[city],
                                category,
                                clicks,
                                impressions,
                                ctr,
                                position,
                                current_date,
                                current_date,
                                current_date
                            ))
                            
                            query_id = cur.fetchone()[0]
                            
                            # Создаем метрики для этого запроса
                            cur.execute("""
                                INSERT INTO daily_metrics
                                (query_id, url, clicks, impressions, ctr, position, date)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT ON CONSTRAINT daily_metrics_unique
                                DO UPDATE SET
                                    clicks = EXCLUDED.clicks,
                                    impressions = EXCLUDED.impressions,
                                    ctr = EXCLUDED.ctr,
                                    position = EXCLUDED.position
                            """, (
                                query_id,
                                f"https://example.com/{category}/{query_id}",
                                clicks,
                                impressions,
                                ctr,
                                position,
                                current_date
                            ))
                            
                            print(f"- {query}: позиция {position:.1f}, CTR {ctr:.1%}")
                
                current_date += timedelta(days=1)

if __name__ == "__main__":
    add_test_data()
