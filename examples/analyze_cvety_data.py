"""Example script for analyzing cvety.kz GSC data."""
import os
from datetime import datetime, timedelta

import pandas as pd

from src.collectors.gsc_collector import GSCCollector
from src.analytics import GSCAnalyzer, Period, Dimension
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def categorize_query(query):
    # Список городов и их вариации
    cities = {
        'алматы': ['алматы', 'almaty'],
        'астана': ['астана', 'astana', 'нур-султан'],
        'шымкент': ['шымкент', 'shymkent'],
        'караганда': ['караганда', 'karaganda'],
        'костанай': ['костанай', 'kostanay'],
        'павлодар': ['павлодар', 'pavlodar'],
        'актау': ['актау', 'aktau'],
        'актобе': ['актобе', 'aktobe'],
        'атырау': ['атырау', 'atyrau'],
        'кокшетау': ['кокшетау', 'kokshetau'],
        'семей': ['семей', 'semey'],
        'тараз': ['тараз', 'taraz'],
        'уральск': ['уральск', 'uralsk'],
        'усть-каменогорск': ['усть-каменогорск', 'ust-kamenogorsk'],
        'петропавловск': ['петропавловск', 'petropavlovsk']
    }
    
    # Типы запросов
    query_types = [
        'доставка цветов',
        'цветы',
        'купить цветы',
        'заказать цветы',
        'магазин цветов',
        'букеты'
    ]
    
    query = query.lower()
    
    # Определяем город
    city = None
    for city_name, variants in cities.items():
        if any(variant in query for variant in variants):
            city = city_name
            break
    
    if not city:
        return None, None
    
    # Определяем тип запроса
    query_type = None
    for qtype in query_types:
        if qtype in query:
            query_type = qtype
            break
    
    if not query_type:
        query_type = 'другое'
    
    return city, query_type

def analyze_city_queries(df):
    # Создаем новые колонки для города и типа запроса
    df['city'], df['query_type'] = zip(*df['query'].apply(categorize_query))
    
    # Фильтруем только запросы с определенным городом
    city_queries = df[df['city'].notna()].copy()
    
    # Агрегируем метрики по городам и типам запросов
    city_stats = city_queries.groupby(['city', 'query_type']).agg({
        'clicks': 'sum',
        'impressions': 'sum',
        'position': 'mean',
        'query': lambda x: list(set(x))  # Уникальные запросы
    }).reset_index()
    
    # Добавляем CTR
    city_stats['ctr'] = city_stats['clicks'] / city_stats['impressions']
    
    return city_stats

def main():
    """Analyze GSC data for cvety.kz."""
    # Initialize collector
    site_url = 'sc-domain:cvety.kz'
    collector = GSCCollector(site_url)
    
    # Set date range for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    logger.info(f"Collecting data from {start_date.date()} to {end_date.date()}")
    
    # Collect data
    data = collector.collect(
        start_date=start_date,
        end_date=end_date,
        dimensions=['query', 'page']
    )
    
    # Convert to DataFrame with proper columns
    df = pd.DataFrame([{
        'query': row['query'],
        'url': row['url'],
        'clicks': row['clicks'],
        'impressions': row['impressions'],
        'ctr': row['ctr'],
        'position': row['position']
    } for row in data])
    
    print("\nData Overview:")
    print("-" * 50)
    print(f"Total rows: {len(df)}")
    
    if not df.empty:
        print("\nTop 10 Queries by Clicks:")
        print(df.nlargest(10, 'clicks')[['query', 'clicks', 'impressions', 'position']])
        
        print("\nTop 10 URLs by Clicks:")
        print(df.nlargest(10, 'clicks')[['url', 'clicks', 'impressions', 'position']])
        
        # Анализ запросов по городам
        print("\nАнализ запросов по городам:")
        print("-" * 50)
        
        city_stats = analyze_city_queries(df)
        
        # Выводим статистику по каждому городу
        for city in city_stats['city'].unique():
            print(f"\n{city.upper()}:")
            city_data = city_stats[city_stats['city'] == city].sort_values('clicks', ascending=False)
            
            total_clicks = city_data['clicks'].sum()
            total_impressions = city_data['impressions'].sum()
            avg_position = city_data['position'].mean()
            
            print(f"Общая статистика:")
            print(f"Клики: {total_clicks}, Показы: {total_impressions}, Средняя позиция: {avg_position:.2f}")
            
            print("\nПо типам запросов:")
            for _, row in city_data.iterrows():
                print(f"\n{row['query_type']}:")
                print(f"Клики: {row['clicks']}, Показы: {row['impressions']}, Позиция: {row['position']:.2f}")
                print("Примеры запросов:", ', '.join(row['query'][:3]))  # Показываем до 3 примеров
        
        # Анализ запросов по доставке в разных городах
        print("\nДоставка цветов по городам:")
        print("-" * 50)
        delivery_queries = df[
            df['query'].str.contains('доставка цветов', case=False, na=False)
        ].sort_values('clicks', ascending=False)
        
        if not delivery_queries.empty:
            print("\nТоп запросы по доставке:")
            print(delivery_queries[['query', 'clicks', 'impressions', 'position']].head(15))
            
            print("\nСтатистика по позициям в выдаче:")
            position_stats = delivery_queries.groupby(
                delivery_queries['position'].apply(lambda x: f"Позиция {int(x)}")
            ).agg({
                'clicks': 'sum',
                'impressions': 'sum',
                'query': 'count'
            }).reset_index()
            position_stats['ctr'] = position_stats['clicks'] / position_stats['impressions']
            position_stats = position_stats.sort_values('position')
            print(position_stats)
        
        print("\nQueries with High Impressions but Low CTR:")
        high_imp_low_ctr = df[
            (df['impressions'] > df['impressions'].median()) & 
            (df['ctr'] < df['ctr'].median())
        ].sort_values('impressions', ascending=False).head(10)
        print(high_imp_low_ctr[['query', 'impressions', 'ctr', 'position']])

    # Save detailed data
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save top queries
    filename = f"top_queries_{start_date.date()}_{end_date.date()}.csv"
    filepath = os.path.join(data_dir, filename)
    df.nlargest(10, 'clicks')[['query', 'clicks', 'impressions', 'position']].to_csv(filepath)
    logger.info(f"Saved top queries to {filepath}")
    
    # Save opportunities
    filename = f"opportunities_{start_date.date()}_{end_date.date()}.csv"
    filepath = os.path.join(data_dir, filename)
    high_imp_low_ctr.to_csv(filepath)
    logger.info(f"Saved opportunities to {filepath}")


if __name__ == '__main__':
    main()
