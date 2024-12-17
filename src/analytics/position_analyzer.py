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
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class PositionChange:
    """Изменение позиции запроса."""
    query: str
    page_url: str
    city: Optional[str]
    old_position: float
    new_position: float
    change: float
    change_abs: float
    impressions_change: int
    clicks_change: int
    query_type: str
    is_seasonal: bool = False
    seasonality_score: float = 0.0
    competitors: List[str] = None

@dataclass
class PeriodStats:
    """Статистика за период."""
    period_days: int
    avg_position: float
    improved_count: int
    declined_count: int
    total_queries: int
    significant_changes: int
    seasonality_affected: int = 0
    competitors_affected: int = 0

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
        start_date: datetime,
        end_date: datetime,
        min_change: float = 3.0,
        city: Optional[str] = None,
        query_type: Optional[str] = None,
        include_seasonality: bool = True,
        include_competitors: bool = True
    ) -> Tuple[List[PositionChange], PeriodStats]:
        """
        Получение изменений позиций за период.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            min_change: Минимальное изменение позиции для учета
            city: Город для фильтрации
            query_type: Тип запроса для фильтрации
            include_seasonality: Включить анализ сезонности
            include_competitors: Включить анализ конкурентов
            
        Returns:
            Tuple[List[PositionChange], PeriodStats]: Изменения позиций и статистика
        """
        try:
            # Базовый SQL запрос
            query = """
            WITH position_data AS (
                SELECT 
                    sq.query,
                    COALESCE(sq.page_url, 'https://cvety.kz') as page_url,
                    CASE 
                        WHEN sq.city IN ('cvety.kz', 'общий') THEN 'main'
                        WHEN sq.city IN ('blog.cvety.kz', 'блог') THEN 'blog'
                        ELSE sq.city
                    END as normalized_city,
                    sq.position,
                    sq.impressions,
                    sq.clicks,
                    sq.query_type,
                    sq.date
                FROM search_queries_daily sq
                WHERE sq.date IN (%s, %s)
            )
            SELECT 
                pd1.query,
                pd1.page_url,
                pd1.normalized_city as city,
                pd1.position as old_position,
                pd2.position as new_position,
                pd1.impressions as old_impressions,
                pd2.impressions as new_impressions,
                pd1.clicks as old_clicks,
                pd2.clicks as new_clicks,
                pd1.query_type
            FROM position_data pd1
            JOIN position_data pd2 
                ON pd1.query = pd2.query 
                AND pd1.page_url = pd2.page_url 
                AND pd1.normalized_city = pd2.normalized_city
                AND pd1.date < pd2.date
            ORDER BY ABS(pd2.position - pd1.position) DESC
            """
            
            params = [start_date, end_date]
            
            # Добавляем фильтры
            if city:
                query += " AND pd1.normalized_city = %s"
                params.append(city)
            if query_type:
                query += " AND pd1.query_type = %s"
                params.append(query_type)
                
            # Получаем данные
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Сначала проверяем данные в position_data
                    cur.execute("""
                        SELECT date, COUNT(*) 
                        FROM search_queries_daily 
                        WHERE date IN (%s, %s)
                        GROUP BY date
                        ORDER BY date
                    """, params)
                    
                    print("\nДанные по датам:")
                    for row in cur.fetchall():
                        print(f"- {row[0]}: {row[1]} записей")
                    
                    # Теперь выполняем основной запрос
                    print("\nВыполняем запрос:", query)
                    print("Параметры:", params)
                    
                    cur.execute(query, params)
                    rows = cur.fetchall()
                    
                    print(f"\nНайдено строк: {len(rows)}")
                    if rows:
                        print("\nПервые 3 строки:")
                        for row in rows[:3]:
                            print(row)
            
            changes: List[PositionChange] = []
            stats = PeriodStats(
                period_days=(end_date - start_date).days,
                avg_position=0,
                improved_count=0,
                declined_count=0,
                total_queries=len(rows),
                significant_changes=0
            )
            
            total_position = 0
            for row in rows:
                old_pos = row[3]
                new_pos = row[4]
                change = old_pos - new_pos  # Положительное значение = улучшение
                change_abs = abs(change)
                
                if change_abs >= min_change:
                    pos_change = PositionChange(
                        query=row[0],
                        page_url=row[1],
                        city=row[2],
                        old_position=old_pos,
                        new_position=new_pos,
                        change=change,
                        change_abs=change_abs,
                        impressions_change=row[6] - row[5],
                        clicks_change=row[8] - row[7],
                        query_type=row[9]
                    )
                    
                    # Анализ сезонности
                    if include_seasonality:
                        seasonality = self._analyze_seasonality(
                            pos_change.query,
                            pos_change.city,
                            start_date
                        )
                        pos_change.is_seasonal = seasonality[0]
                        pos_change.seasonality_score = seasonality[1]
                        if pos_change.is_seasonal:
                            stats.seasonality_affected += 1
                    
                    # Анализ конкурентов
                    if include_competitors:
                        competitors = self._analyze_competitors(
                            pos_change.query,
                            pos_change.page_url,
                            pos_change.city,
                            start_date,
                            end_date
                        )
                        pos_change.competitors = competitors
                        if competitors:
                            stats.competitors_affected += 1
                    
                    changes.append(pos_change)
                    stats.significant_changes += 1
                    
                    if change > 0:
                        stats.improved_count += 1
                    else:
                        stats.declined_count += 1
                
                total_position += new_pos
            
            if stats.total_queries > 0:
                stats.avg_position = total_position / stats.total_queries
            
            return changes, stats
            
        except Exception as e:
            logger.error(f"Error in get_position_changes: {str(e)}")
            raise

    def get_weekly_changes(
        self,
        end_date: datetime,
        weeks_back: int = 4,
        **kwargs
    ) -> List[Tuple[datetime, List[PositionChange], PeriodStats]]:
        """
        Получение еженедельных изменений позиций.
        
        Args:
            end_date: Конечная дата
            weeks_back: Количество недель для анализа
            **kwargs: Дополнительные параметры для get_position_changes
            
        Returns:
            List[Tuple[datetime, List[PositionChange], PeriodStats]]: 
            Список кортежей (дата, изменения, статистика) для каждой недели
        """
        try:
            weekly_data = []
            for week in range(weeks_back):
                week_end = end_date - timedelta(days=week*7)
                week_start = week_end - timedelta(days=7)
                
                changes, stats = self.get_position_changes(
                    start_date=week_start,
                    end_date=week_end,
                    **kwargs
                )
                weekly_data.append((week_start, changes, stats))
            
            return weekly_data
            
        except Exception as e:
            logger.error(f"Error in get_weekly_changes: {str(e)}")
            raise

    def get_changes_statistics(self, changes: list) -> dict:
        """Получение статистики по изменениям позиций."""
        stats = {
            'total': len(changes),
            'significant': 0,
            'improvements': 0,
            'deteriorations': 0,
            'avg_position': 0
        }
        
        if not changes:
            return stats
            
        # Считаем статистику
        total_position = 0
        for change in changes:
            position_diff = change['old_position'] - change['new_position']
            if abs(position_diff) >= 3:  # Значимое изменение
                stats['significant'] += 1
                if position_diff > 0:  # Улучшение
                    stats['improvements'] += 1
                else:  # Ухудшение
                    stats['deteriorations'] += 1
            total_position += change['new_position']
            
        # Средняя позиция
        stats['avg_position'] = total_position / len(changes)
        
        return stats

    def _analyze_seasonality(
        self,
        query: str,
        city: Optional[str],
        current_date: datetime
    ) -> Tuple[bool, float]:
        """
        Анализ сезонности запроса.
        
        Args:
            query: Поисковый запрос
            city: Город
            current_date: Текущая дата
            
        Returns:
            Tuple[bool, float]: (является ли сезонным, оценка сезонности)
        """
        try:
            # Получаем данные за прошлый год
            year_ago = current_date - timedelta(days=365)
            query = """
            SELECT 
                date_trunc('week', date) as week,
                AVG(impressions) as avg_impressions
            FROM search_queries_daily
            WHERE query = %s
                AND date BETWEEN %s AND %s
            """
            params = [query, year_ago, current_date]
            
            if city:
                query += " AND city = %s"
                params.append(city)
                
            query += """
            GROUP BY week
            ORDER BY week
            """
            
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    rows = cur.fetchall()
            
            if not rows:
                return False, 0.0
            
            # Преобразуем в pandas Series для анализа
            data = pd.Series([row[1] for row in rows])
            
            # Вычисляем коэффициент вариации
            cv = data.std() / data.mean() if data.mean() > 0 else 0
            
            # Проверяем наличие сезонного паттерна
            is_seasonal = cv > 0.3  # Высокая вариативность может указывать на сезонность
            seasonality_score = min(cv, 1.0)  # Нормализуем оценку от 0 до 1
            
            return is_seasonal, seasonality_score
            
        except Exception as e:
            logger.error(f"Error in _analyze_seasonality: {str(e)}")
            return False, 0.0

    def _analyze_competitors(
        self,
        query: str,
        page_url: str,
        city: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[str]:
        """
        Анализ конкурентов по запросу.
        
        Args:
            query: Поисковый запрос
            page_url: URL страницы
            city: Город
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            List[str]: Список URL конкурентов, которые улучшили позиции
        """
        try:
            # Получаем данные о конкурентах
            query = """
            WITH our_positions AS (
                SELECT position
                FROM search_queries_daily
                WHERE query = %s
                    AND page_url = %s
                    AND date BETWEEN %s AND %s
            """
            params = [query, page_url, start_date, end_date]
            
            if city:
                query += " AND city = %s"
                params.append(city)
                
            query += """
            ),
            competitor_changes AS (
                SELECT 
                    sq.page_url,
                    AVG(sq.position) as avg_position,
                    MIN(sq.position) as best_position
                FROM search_queries_daily sq
                WHERE sq.query = %s
                    AND sq.page_url != %s
                    AND sq.date BETWEEN %s AND %s
            """
            params.extend([query, page_url, start_date, end_date])
            
            if city:
                query += " AND sq.city = %s"
                params.append(city)
                
            query += """
                GROUP BY sq.page_url
                HAVING MIN(sq.position) < (SELECT AVG(position) FROM our_positions)
                ORDER BY avg_position ASC
                LIMIT 5
            )
            SELECT page_url
            FROM competitor_changes
            """
            
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    rows = cur.fetchall()
            
            return [row[0] for row in rows]
            
        except Exception as e:
            logger.error(f"Error in _analyze_competitors: {str(e)}")
            return []

    def analyze_positions(
        self,
        days: List[int] = [1, 7, 30, 60],
        min_change: float = 3.0,
        query_type: Optional[str] = None,
        url_pattern: Optional[str] = None,
        include_seasonality: bool = True,
        include_competitors: bool = True
    ) -> Dict[str, Any]:
        """
        Комплексный анализ позиций.
        
        Args:
            days: Список периодов для анализа в днях
            min_change: Минимальное изменение позиции для учета
            query_type: Тип запроса для фильтрации
            url_pattern: Паттерн URL для фильтрации
            include_seasonality: Включить анализ сезонности
            include_competitors: Включить анализ конкурентов
            
        Returns:
            Dict[str, Any]: Словарь с результатами анализа
        """
        current_date = datetime.now()
        
        # Анализируем каждый период
        period_stats = {}
        for days_back in days:
            start_date = current_date - timedelta(days=days_back)
            changes, stats = self.get_position_changes(
                start_date=start_date,
                end_date=current_date,
                min_change=min_change,
                query_type=query_type,
                include_seasonality=include_seasonality,
                include_competitors=include_competitors
            )
            period_stats[days_back] = {'changes': changes, 'stats': stats}
        
        # Формируем общую сводку
        summary = {
            'analyzed_periods': days,
            'min_change_threshold': min_change,
            'query_type_filter': query_type,
            'url_pattern_filter': url_pattern,
            'include_seasonality': include_seasonality,
            'include_competitors': include_competitors
        }
        
        return {
            'periods': period_stats,
            'summary': summary
        }
