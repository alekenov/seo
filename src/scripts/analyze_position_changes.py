"""Скрипт для анализа изменений позиций в поисковой выдаче."""
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class PositionChange:
    """Класс для хранения информации об изменении позиции."""
    query: str
    url: str
    old_position: float
    new_position: float
    position_change: float
    old_clicks: int
    new_clicks: int
    clicks_change: int
    old_impressions: int
    new_impressions: int
    impressions_change: int

def get_position_data(
    db: PostgresClient,
    start_date: datetime,
    end_date: datetime
) -> List[Dict[str, Any]]:
    """Получение данных о позициях из базы за указанный период.
    
    Args:
        db: Клиент базы данных
        start_date: Начальная дата
        end_date: Конечная дата
        
    Returns:
        List[Dict]: Список данных по позициям
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    query,
                    url,
                    position,
                    clicks,
                    impressions,
                    date_collected
                FROM search_queries 
                WHERE date_collected BETWEEN %s AND %s
                ORDER BY clicks DESC
            """, (start_date.date(), end_date.date()))
            
            rows = []
            for row in cur.fetchall():
                rows.append({
                    'query': row[0],
                    'url': row[1],
                    'position': float(row[2]),
                    'clicks': int(row[3]),
                    'impressions': int(row[4]),
                    'date_collected': row[5]
                })
            
            return rows

def analyze_position_changes(
    current_data: List[Dict[str, Any]],
    previous_data: List[Dict[str, Any]],
    min_position_change: float = 2.0,
    min_clicks: int = 5
) -> List[PositionChange]:
    """Анализ изменений позиций.
    
    Args:
        current_data: Текущие данные
        previous_data: Данные за предыдущий период
        min_position_change: Минимальное изменение позиции для учета
        min_clicks: Минимальное количество кликов для учета
        
    Returns:
        List[PositionChange]: Список значимых изменений
    """
    # Создаем словари для быстрого поиска
    previous_dict = {
        (row['query'], row['url']): row
        for row in previous_data
    }
    
    changes = []
    
    for current_row in current_data:
        query = current_row['query']
        url = current_row['url']
        key = (query, url)
        
        if key in previous_dict:
            prev_row = previous_dict[key]
            position_change = prev_row['position'] - current_row['position']
            
            # Проверяем, является ли изменение значимым
            if (abs(position_change) >= min_position_change and
                (current_row['clicks'] >= min_clicks or prev_row['clicks'] >= min_clicks)):
                
                change = PositionChange(
                    query=query,
                    url=url,
                    old_position=prev_row['position'],
                    new_position=current_row['position'],
                    position_change=position_change,
                    old_clicks=prev_row['clicks'],
                    new_clicks=current_row['clicks'],
                    clicks_change=current_row['clicks'] - prev_row['clicks'],
                    old_impressions=prev_row['impressions'],
                    new_impressions=current_row['impressions'],
                    impressions_change=current_row['impressions'] - prev_row['impressions']
                )
                changes.append(change)
    
    # Сортируем по абсолютному значению изменения позиции
    return sorted(changes, key=lambda x: abs(x.position_change), reverse=True)

def format_change(value: float, is_position: bool = False) -> str:
    """Форматирование изменения для вывода."""
    if is_position:
        # Для позиций уменьшение - это улучшение
        sign = "⬆️" if value < 0 else "⬇️"
    else:
        # Для кликов и показов увеличение - это улучшение
        sign = "⬆️" if value > 0 else "⬇️"
    
    return f"{sign}{abs(value):.1f}"

def main():
    """Основная функция."""
    db = PostgresClient()
    
    # Получаем данные за текущий и предыдущий периоды (30 дней)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    prev_start_date = start_date - timedelta(days=30)
    
    logger.info(f"Загружаем данные за текущий период ({start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')})...")
    current_data = get_position_data(db, start_date, end_date)
    
    logger.info(f"Загружаем данные за предыдущий период ({prev_start_date.strftime('%Y-%m-%d')} - {start_date.strftime('%Y-%m-%d')})...")
    previous_data = get_position_data(db, prev_start_date, start_date)
    
    # Анализируем изменения
    changes = analyze_position_changes(
        current_data,
        previous_data,
        min_position_change=2.0,  # Изменение позиции на 2 и более
        min_clicks=5  # Минимум 5 кликов
    )
    
    if not changes:
        logger.info("Значимых изменений позиций не обнаружено")
        return
    
    # Группируем изменения по URL
    url_changes: Dict[str, List[PositionChange]] = {}
    for change in changes:
        if change.url not in url_changes:
            url_changes[change.url] = []
        url_changes[change.url].append(change)
    
    # Выводим результаты
    logger.info(f"\nАнализ изменений позиций за период {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}:")
    logger.info("=" * 80)
    
    for url, url_changes_list in url_changes.items():
        logger.info(f"\nURL: {url}")
        logger.info("-" * 80)
        
        for change in url_changes_list:
            logger.info(
                f"Запрос: {change.query}\n"
                f"Позиция: {change.new_position:.1f} ({format_change(change.position_change, True)})\n"
                f"Клики: {change.new_clicks} ({format_change(change.clicks_change)})\n"
                f"Показы: {change.new_impressions} ({format_change(change.impressions_change)})\n"
            )

if __name__ == "__main__":
    main()
