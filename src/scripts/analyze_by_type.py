"""Анализ изменений позиций по типам запросов."""
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_query_data(db: PostgresClient, start_date: datetime, end_date: datetime) -> List[Dict]:
    """Получение данных по запросам за период."""
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    query,
                    query_type,
                    AVG(position) as avg_position,
                    SUM(clicks) as total_clicks,
                    SUM(impressions) as total_impressions,
                    AVG(ctr) as avg_ctr,
                    date_collected
                FROM search_queries
                WHERE date_collected BETWEEN %s AND %s
                GROUP BY query, query_type, date_collected
                ORDER BY total_clicks DESC
            """, (start_date, end_date))
            
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]

def analyze_position_changes(current_data: List[Dict], previous_data: List[Dict]) -> Dict[str, List[Dict]]:
    """Анализ изменений позиций по типам запросов."""
    # Группируем данные по запросам
    current_by_query = {(row['query'], row['query_type']): row for row in current_data}
    previous_by_query = {(row['query'], row['query_type']): row for row in previous_data}
    
    # Анализируем изменения по каждому типу
    changes_by_type: Dict[str, List[Dict]] = {
        'доставка_город': [],
        'доставка_общий': [],
        'коммерческий': [],
        'информационный': [],
        'прочее': [],
        'навигационный': []  # Добавляем для обратной совместимости
    }
    
    # Анализируем все запросы из текущего периода
    for (query, query_type), current in current_by_query.items():
        if (query, query_type) in previous_by_query:
            previous = previous_by_query[(query, query_type)]
            
            # Рассчитываем изменения
            position_change = previous['avg_position'] - current['avg_position']
            clicks_change = current['total_clicks'] - previous['total_clicks']
            impressions_change = current['total_impressions'] - previous['total_impressions']
            
            # Добавляем значительные изменения
            if abs(position_change) >= 3 or abs(clicks_change) >= 5:
                change_info = {
                    'query': query,
                    'current_position': round(current['avg_position'], 1),
                    'position_change': round(position_change, 1),
                    'current_clicks': current['total_clicks'],
                    'clicks_change': clicks_change,
                    'current_impressions': current['total_impressions'],
                    'impressions_change': impressions_change
                }
                changes_by_type[query_type].append(change_info)
    
    return changes_by_type

def main():
    """Main function."""
    try:
        # Инициализируем клиент базы данных
        db = PostgresClient()
        
        # Определяем периоды для анализа
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        prev_end_date = start_date
        prev_start_date = prev_end_date - timedelta(days=30)
        
        # Получаем данные за оба периода
        current_data = get_query_data(db, start_date, end_date)
        previous_data = get_query_data(db, prev_start_date, prev_end_date)
        
        # Анализируем изменения
        changes = analyze_position_changes(current_data, previous_data)
        
        # Выводим результаты
        for query_type, type_changes in changes.items():
            if type_changes:
                logger.info(f"\nИзменения для типа '{query_type}':")
                for change in sorted(type_changes, key=lambda x: abs(x['position_change']), reverse=True):
                    logger.info(f"\nЗапрос: {change['query']}")
                    logger.info(f"Текущая позиция: {change['current_position']} (изменение: {change['position_change']:+.1f})")
                    logger.info(f"Клики: {change['current_clicks']} (изменение: {change['clicks_change']:+d})")
                    logger.info(f"Показы: {change['current_impressions']} (изменение: {change['impressions_change']:+d})")
            else:
                logger.info(f"\nНет значительных изменений для типа '{query_type}'")
                
    except Exception as e:
        logger.error(f"Ошибка при анализе данных: {e}")
        raise

if __name__ == "__main__":
    main()
