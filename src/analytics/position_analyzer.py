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
    category: Optional[str]
    old_position: float
    new_position: float
    change: float
    trend: str  # up, down, stable
    significance: str  # high, medium, low

@dataclass
class CategoryStats:
    """Статистика по категории."""
    avg_position: float
    total_queries: int
    improved_queries: int
    declined_queries: int
    problematic_urls: List[str]
    top_gainers: List[PositionChange]
    top_losers: List[PositionChange]

class EnhancedPositionAnalyzer:
    """Улучшенный анализатор позиций."""
    
    def __init__(self, db_client: PostgresClient):
        """
        Инициализация анализатора.
        
        Args:
            db_client: Клиент базы данных PostgreSQL
        """
        self.db = db_client
        
    def analyze_positions(
        self,
        days: int = 30,
        min_change: float = 3.0,
        category: Optional[str] = None,
        url_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Комплексный анализ позиций.
        
        Args:
            days: Количество дней для анализа
            min_change: Минимальное значимое изменение позиции
            category: Фильтр по категории
            url_pattern: Фильтр по URL (поддерживает LIKE)
            
        Returns:
            Словарь с результатами анализа:
            - summary: общая статистика
            - period_comparison: сравнение периодов (7д и 30д)
            - significant_changes: значимые изменения
            - trends: тренды по категориям/URL
            - anomalies: обнаруженные аномалии
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Базовый запрос
        query = """
        WITH daily_stats AS (
            SELECT 
                sq.query,
                sq.id as query_id,
                dm.url,
                c.name as city,
                dm.date,
                dm.position,
                FIRST_VALUE(dm.position) OVER (
                    PARTITION BY sq.query 
                    ORDER BY dm.date
                ) as first_position,
                FIRST_VALUE(dm.position) OVER (
                    PARTITION BY sq.query 
                    ORDER BY dm.date DESC
                ) as last_position,
                AVG(dm.position) OVER (
                    PARTITION BY sq.query
                ) as avg_position,
                STDDEV(dm.position) OVER (
                    PARTITION BY sq.query
                ) as position_stddev
            FROM search_queries sq
            JOIN daily_metrics dm ON sq.id = dm.query_id
            LEFT JOIN cities c ON sq.city_id = c.id
            WHERE dm.date BETWEEN %s AND %s
        )
        SELECT * FROM daily_stats
        """
        
        # Добавляем фильтры
        params = [start_date, end_date]
        if category:
            query = query.replace(
                "SELECT * FROM daily_stats",
                "SELECT * FROM daily_stats WHERE category = %s"
            )
            params.append(category)
        if url_pattern:
            query = query.replace(
                "SELECT * FROM daily_stats",
                "SELECT * FROM daily_stats WHERE url LIKE %s"
            )
            params.append(f"%{url_pattern}%")
            
        # Получаем данные
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                
        # Преобразуем в DataFrame
        df = pd.DataFrame(rows, columns=[
            'query', 'query_id', 'url', 'city', 'date', 'position',
            'first_position', 'last_position', 'avg_position', 'position_stddev'
        ])
        
        if df.empty:
            return {
                'summary': {
                    'total_queries': 0,
                    'total_urls': 0,
                    'avg_position': 0,
                    'improved_queries': 0,
                    'declined_queries': 0,
                    'stable_queries': 0
                },
                'period_comparison': {
                    'last_7d_avg': 0,
                    'prev_7d_avg': 0,
                    'improved_7d': 0,
                    'declined_7d': 0,
                    'top_gainers_7d': [],
                    'top_losers_7d': []
                },
                'significant_changes': {
                    'improved': [],
                    'declined': []
                },
                'trends': {
                    'problematic_urls': [],
                    'url_trends': [],
                    'city_trends': []
                },
                'anomalies': []
            }
        
        # Анализируем данные
        results = {
            'summary': self._get_summary_stats(df),
            'period_comparison': self._compare_periods(df),
            'significant_changes': self._get_significant_changes(df, min_change),
            'trends': self._analyze_trends(df),
            'anomalies': self._detect_anomalies(df)
        }
        
        return results
    
    def _get_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Получение общей статистики."""
        return {
            'total_queries': df['query'].nunique(),
            'total_urls': df['url'].nunique(),
            'avg_position': df['position'].mean(),
            'improved_queries': len(df[df['last_position'] < df['first_position']]['query'].unique()),
            'declined_queries': len(df[df['last_position'] > df['first_position']]['query'].unique()),
            'stable_queries': len(df[df['last_position'] == df['first_position']]['query'].unique())
        }
    
    def _compare_periods(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Сравнение периодов (7д и 30д)."""
        now = datetime.now().date()
        
        # Последние 7 дней
        last_7d = df[df['date'] >= now - timedelta(days=7)]
        last_7d_avg = last_7d.groupby('query')['position'].mean()
        
        # Предыдущие 7 дней
        prev_7d = df[
            (df['date'] >= now - timedelta(days=14)) &
            (df['date'] < now - timedelta(days=7))
        ]
        prev_7d_avg = prev_7d.groupby('query')['position'].mean()
        
        # Сравниваем периоды
        changes_7d = pd.DataFrame({
            'current': last_7d_avg,
            'previous': prev_7d_avg
        }).dropna()
        
        changes_7d['change'] = changes_7d['previous'] - changes_7d['current']
        
        return {
            'last_7d_avg': last_7d['position'].mean(),
            'prev_7d_avg': prev_7d['position'].mean(),
            'improved_7d': len(changes_7d[changes_7d['change'] > 0]),
            'declined_7d': len(changes_7d[changes_7d['change'] < 0]),
            'top_gainers_7d': self._format_position_changes(
                changes_7d.nlargest(5, 'change')
            ),
            'top_losers_7d': self._format_position_changes(
                changes_7d.nsmallest(5, 'change')
            )
        }
    
    def _get_significant_changes(
        self,
        df: pd.DataFrame,
        min_change: float
    ) -> Dict[str, List[PositionChange]]:
        """Получение значимых изменений позиций."""
        # Считаем изменения для каждого запроса
        changes = df.groupby('query').agg({
            'first_position': 'first',
            'last_position': 'first',
            'url': 'first',
            'position_stddev': 'first'
        }).reset_index()
        
        changes['change'] = changes['first_position'] - changes['last_position']
        
        # Определяем значимость изменения
        def get_significance(row):
            if abs(row['change']) >= min_change * 2:
                return 'high'
            elif abs(row['change']) >= min_change:
                return 'medium'
            return 'low'
            
        changes['significance'] = changes.apply(get_significance, axis=1)
        
        # Фильтруем значимые изменения
        significant = changes[changes['significance'] != 'low']
        
        # Форматируем результаты
        return {
            'improved': self._format_position_changes(
                significant[significant['change'] > 0]
            ),
            'declined': self._format_position_changes(
                significant[significant['change'] < 0]
            )
        }
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Анализ трендов в позициях."""
        # Группируем по URL для анализа страниц
        url_trends = df.groupby('url').agg({
            'position': ['mean', 'std', 'count'],
            'query': 'nunique'
        }).reset_index()
        
        # Находим проблемные URL
        problematic_urls = url_trends[
            (url_trends[('position', 'mean')] > 10) &  # Плохие позиции
            (url_trends[('query', 'nunique')] > 5)     # Много запросов
        ]
        
        # Анализируем тренды по городам
        city_trends = df.groupby('city').agg({
            'position': ['mean', 'std'],
            'query': 'nunique',
            'url': 'nunique'
        }).reset_index()
        
        return {
            'problematic_urls': problematic_urls['url'].tolist(),
            'url_trends': self._format_url_trends(url_trends),
            'city_trends': self._format_city_trends(city_trends)
        }
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Обнаружение аномалий в позициях."""
        anomalies = []
        
        # Группируем по запросу
        for query, group in df.groupby('query'):
            positions = group['position'].values
            
            # Проверяем на резкие изменения
            if len(positions) > 1:
                changes = np.diff(positions)
                mean_change = np.mean(changes)
                std_change = np.std(changes)
                
                for i, change in enumerate(changes):
                    # Считаем аномальным изменение более 2 стандартных отклонений
                    if abs(change - mean_change) > 2 * std_change:
                        anomalies.append({
                            'query': query,
                            'date': group['date'].iloc[i+1],
                            'old_position': positions[i],
                            'new_position': positions[i+1],
                            'change': change,
                            'significance': 'high' if abs(change) > 5 else 'medium'
                        })
        
        return anomalies
    
    def _format_position_changes(
        self,
        changes: pd.DataFrame
    ) -> List[PositionChange]:
        """Форматирование изменений позиций."""
        result = []
        for idx in changes.index:
            try:
                result.append(PositionChange(
                    query=str(idx),  # Индекс - это query
                    url="",  # URL может быть пустым для сравнения периодов
                    category=None,
                    old_position=float(changes.loc[idx, 'previous']),
                    new_position=float(changes.loc[idx, 'current']),
                    change=float(changes.loc[idx, 'change']),
                    trend='up' if changes.loc[idx, 'change'] > 0 else 'down',
                    significance='high' if abs(changes.loc[idx, 'change']) >= 5 else 'medium'
                ))
            except (KeyError, ValueError) as e:
                print(f"Ошибка при форматировании изменения: {e}")
                continue
        return result
    
    def _format_url_trends(self, trends: pd.DataFrame) -> List[Dict[str, Any]]:
        """Форматирование трендов по URL."""
        return [
            {
                'url': row['url'],
                'avg_position': row[('position', 'mean')],
                'position_std': row[('position', 'std')],
                'queries_count': row[('query', 'nunique')],
                'stability': 'stable' if row[('position', 'std')] < 2 else 'unstable'
            }
            for _, row in trends.iterrows()
        ]
    
    def _format_city_trends(self, trends: pd.DataFrame) -> List[Dict[str, Any]]:
        """Форматирование трендов по городам."""
        return [
            {
                'city': row['city'],
                'avg_position': row[('position', 'mean')],
                'position_std': row[('position', 'std')],
                'queries_count': row[('query', 'nunique')],
                'urls_count': row[('url', 'nunique')]
            }
            for _, row in trends.iterrows()
        ]
