"""
Улучшенный анализатор позиций в поисковой выдаче.
Включает сравнение по периодам, анализ трендов и выявление аномалий.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass
from src.database.postgres_client import PostgresClient

@dataclass
class PositionChange:
    """Изменение позиции запроса."""
    query: str
    url: str
    city: Optional[str]
    old_position: float
    new_position: float
    change: float
    change_abs: float
    impressions_change: int
    clicks_change: int
    query_type: str

@dataclass
class PeriodStats:
    """Статистика за период."""
    period_days: int
    avg_position: float
    improved_count: int
    declined_count: int
    total_queries: int
    significant_changes: int

class EnhancedPositionAnalyzer:
    """Улучшенный анализатор позиций."""
    
    def __init__(self, db_client: PostgresClient):
        """
        Инициализация анализатора.
        
        Args:
            db_client: Клиент базы данных PostgreSQL
        """
        self.db = db_client
        
    def get_position_changes(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        min_change: float = 3.0,
        query_type: Optional[str] = None,
        url_pattern: Optional[str] = None
    ) -> List[PositionChange]:
        """
        Получение изменений позиций за период.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            min_change: Минимальное значимое изменение
            query_type: Тип запроса для фильтрации
            url_pattern: Паттерн URL для фильтрации
            
        Returns:
            Список изменений позиций
        """
        query = """
        SELECT * FROM get_position_changes(%s, %s, %s, %s, %s)
        """
        results = self.db.fetch_all(
            query,
            (start_date, end_date, min_change, query_type, url_pattern)
        )
        
        return [
            PositionChange(
                query=row['query'],
                url=row['url'],
                city=row['city_name'],
                old_position=row['old_position'],
                new_position=row['new_position'],
                change=row['position_change'],
                change_abs=row['position_change_abs'],
                impressions_change=row['impressions_change'],
                clicks_change=row['clicks_change'],
                query_type=row['query_type']
            )
            for row in results
        ]
    
    def get_period_stats(
        self,
        current_date: datetime.date,
        periods: List[int] = [1, 7, 30, 60]
    ) -> Dict[int, PeriodStats]:
        """
        Получение статистики по разным периодам.
        
        Args:
            current_date: Текущая дата
            periods: Список периодов в днях
            
        Returns:
            Словарь со статистикой по периодам
        """
        query = """
        SELECT * FROM get_position_stats(%s, %s::integer[])
        """
        results = self.db.fetch_all(query, (current_date, periods))
        
        return {
            row['period_days']: PeriodStats(
                period_days=row['period_days'],
                avg_position=row['avg_position'],
                improved_count=row['improved_count'],
                declined_count=row['declined_count'],
                total_queries=row['total_queries'],
                significant_changes=row['significant_changes']
            )
            for row in results
        }
    
    def analyze_positions(
        self,
        days: List[int] = [1, 7, 30, 60],
        min_change: float = 3.0,
        query_type: Optional[str] = None,
        url_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Комплексный анализ позиций.
        
        Args:
            days: Список периодов для анализа в днях
            min_change: Минимальное значимое изменение позиции
            query_type: Фильтр по типу запроса
            url_pattern: Фильтр по URL (поддерживает LIKE)
            
        Returns:
            Словарь с результатами анализа:
            - changes: изменения позиций по периодам
            - stats: статистика по периодам
            - summary: общая сводка
        """
        current_date = datetime.now().date()
        
        # Получаем статистику по всем периодам
        period_stats = self.get_period_stats(current_date, days)
        
        # Получаем изменения для каждого периода
        period_changes = {}
        for days_back in days:
            start_date = current_date - timedelta(days=days_back)
            changes = self.get_position_changes(
                start_date,
                current_date,
                min_change,
                query_type,
                url_pattern
            )
            period_changes[days_back] = changes
        
        # Формируем общую сводку
        summary = {
            'total_analyzed_periods': len(days),
            'current_date': current_date.isoformat(),
            'min_change_threshold': min_change,
            'query_type_filter': query_type,
            'url_pattern_filter': url_pattern,
        }
        
        return {
            'changes': period_changes,
            'stats': period_stats,
            'summary': summary
        }
