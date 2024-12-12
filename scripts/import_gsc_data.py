import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
import re

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

def categorize_query(query):
    """Категоризация запроса"""
    query = query.lower()
    
    if any(word in query for word in ['доставка', 'delivery', 'заказать']):
        return 'delivery'
    elif any(word in query for word in ['букет', 'bouquet']):
        return 'bouquets'
    elif any(word in query for word in ['подарок', 'подарить', 'gift']):
        return 'gifts'
    elif any(word in query for word in ['цветы', 'розы', 'пионы', 'flowers', 'roses']):
        return 'flowers'
    else:
        return 'other'

def extract_city(query):
    """Извлечение города из запроса"""
    cities = {
        'алматы': 'Алматы',
        'астана': 'Астана',
        'нур-султан': 'Астана',
        'шымкент': 'Шымкент',
        'караганда': 'Караганда',
        'костанай': 'Костанай',
        'павлодар': 'Павлодар',
        'актобе': 'Актобе',
        'тараз': 'Тараз',
        'семей': 'Семей',
        'атырау': 'Атырау',
        'almaty': 'Алматы',
        'astana': 'Астана',
        'shymkent': 'Шымкент',
        'karaganda': 'Караганда'
    }
    
    query = query.lower()
    for city_key, city_name in cities.items():
        if city_key in query:
            return city_name
    return None

def add_cities(cursor):
    """Добавление городов из запросов"""
    cities = {
        'Алматы': 'Almaty',
        'Астана': 'Astana',
        'Шымкент': 'Shymkent',
        'Караганда': 'Karaganda',
        'Костанай': 'Kostanay',
        'Павлодар': 'Pavlodar',
        'Актобе': 'Aktobe',
        'Тараз': 'Taraz',
        'Семей': 'Semey',
        'Атырау': 'Atyrau'
    }
    
    city_ids = {}
    for city_name, city_name_en in cities.items():
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

def process_queries(cursor, city_ids):
    """Обработка и импорт поисковых запросов"""
    # Читаем CSV файл
    df = pd.read_csv('/Users/alekenov/CascadeProjects/seobot/dataset/Queries.csv')
    
    # Конвертируем CTR и Position в числовые значения
    df['CTR'] = df['CTR'].str.rstrip('%').astype(float) / 100
    
    query_ids = {}
    queries_data = []
    
    for _, row in df.iterrows():
        query = row['Top queries']
        city = extract_city(query)
        city_id = city_ids.get(city) if city else None
        query_type = categorize_query(query)
        
        print(f"Обрабатываем запрос [{query_type}]: {query}")
        
        cursor.execute("""
            INSERT INTO search_queries 
            (query, city_id, query_type, clicks, impressions, ctr, position, created_at, updated_at, date_collected)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), CURRENT_DATE)
            ON CONFLICT (query, COALESCE(city_id, -1), date_collected) DO UPDATE 
            SET query_type = EXCLUDED.query_type,
                clicks = EXCLUDED.clicks,
                impressions = EXCLUDED.impressions,
                ctr = EXCLUDED.ctr,
                position = EXCLUDED.position
            RETURNING id
        """, (
            query, 
            city_id,
            query_type,
            row['Clicks'],
            row['Impressions'],
            row['CTR'],
            row['Position'],
        ))
        
        query_ids[query] = cursor.fetchone()[0]
    
    return query_ids

def process_pages(cursor, query_ids):
    """Обработка и импорт страниц"""
    # Читаем CSV файл
    df = pd.read_csv('/Users/alekenov/CascadeProjects/seobot/dataset/Pages.csv')
    
    # Конвертируем CTR в числовые значения
    df['CTR'] = df['CTR'].str.rstrip('%').astype(float) / 100
    
    for _, row in df.iterrows():
        url = row['Top pages']
        print(f"Обрабатываем страницу: {url}")
        
        # Добавляем метрики для URL
        cursor.execute("""
            INSERT INTO daily_metrics 
            (date, url, clicks, impressions, position, ctr, created_at, updated_at)
            VALUES (CURRENT_DATE, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (date) DO UPDATE 
            SET clicks = EXCLUDED.clicks,
                impressions = EXCLUDED.impressions,
                position = EXCLUDED.position,
                ctr = EXCLUDED.ctr
        """, (
            url,
            row['Clicks'],
            row['Impressions'],
            row['Position'],
            row['CTR']
        ))

def main():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        print("Добавляем города...")
        city_ids = add_cities(cursor)
        conn.commit()
        
        print("\nОбрабатываем поисковые запросы...")
        query_ids = process_queries(cursor, city_ids)
        conn.commit()
        
        print("\nОбрабатываем страницы...")
        process_pages(cursor, query_ids)
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
