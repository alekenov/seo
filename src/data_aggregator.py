from datetime import datetime, timedelta
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
import numpy as np
from scipy import stats

class DataAggregator:
    def __init__(self):
        """
        Инициализация агрегатора данных с прямым подключением к PostgreSQL
        """
        self.conn = psycopg2.connect(
            dbname="postgres",
            user="postgres.jvfjxlpplbyrafasobzl",
            password="fogdif-7voHxi-ryfqug",
            host="aws-0-eu-central-1.pooler.supabase.com",
            port="6543"
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def __del__(self):
        """
        Закрываем соединение при удалении объекта
        """
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()

    def aggregate_daily_to_weekly(self, start_date: datetime, end_date: datetime) -> None:
        """
        Агрегация ежедневных метрик в недельные
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
        """
        weekly_query = """
            WITH weekly_aggregation AS (
                SELECT 
                    query_id,
                    date_trunc('week', date) as week_start,
                    SUM(clicks) as total_clicks,
                    AVG(clicks) as avg_clicks,
                    SUM(impressions) as total_impressions,
                    AVG(impressions) as avg_impressions,
                    AVG(position) as avg_position,
                    AVG(ctr) as avg_ctr
                FROM daily_metrics
                WHERE date >= %s AND date <= %s
                GROUP BY query_id, date_trunc('week', date)
            )
            INSERT INTO weekly_metrics 
            (week_start, query_id, total_clicks, avg_clicks, 
             total_impressions, avg_impressions, avg_position, avg_ctr)
            SELECT 
                week_start::date,
                query_id,
                total_clicks,
                avg_clicks,
                total_impressions,
                avg_impressions,
                avg_position,
                avg_ctr
            FROM weekly_aggregation
            ON CONFLICT (week_start, query_id) 
            DO UPDATE SET
                total_clicks = EXCLUDED.total_clicks,
                avg_clicks = EXCLUDED.avg_clicks,
                total_impressions = EXCLUDED.total_impressions,
                avg_impressions = EXCLUDED.avg_impressions,
                avg_position = EXCLUDED.avg_position,
                avg_ctr = EXCLUDED.avg_ctr
        """
        
        try:
            self.cursor.execute(weekly_query, (start_date.date(), end_date.date()))
            self.conn.commit()
            print("Агрегация успешно выполнена")
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при агрегации: {str(e)}")
            raise

    def aggregate_weekly_to_monthly(self, start_date: datetime, end_date: datetime) -> None:
        """
        Агрегация недельных метрик в месячные
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
        """
        monthly_query = """
            WITH monthly_aggregation AS (
                SELECT 
                    query_id,
                    date_trunc('month', week_start) as month_start,
                    SUM(total_clicks) as total_clicks,
                    AVG(avg_clicks) as avg_clicks,
                    SUM(total_impressions) as total_impressions,
                    AVG(avg_impressions) as avg_impressions,
                    AVG(avg_position) as avg_position,
                    AVG(avg_ctr) as avg_ctr
                FROM weekly_metrics
                WHERE week_start >= %s AND week_start <= %s
                GROUP BY query_id, date_trunc('month', week_start)
            )
            INSERT INTO monthly_metrics 
            (month_start, query_id, total_clicks, avg_clicks, 
             total_impressions, avg_impressions, avg_position, avg_ctr)
            SELECT 
                month_start::date,
                query_id,
                total_clicks,
                avg_clicks,
                total_impressions,
                avg_impressions,
                avg_position,
                avg_ctr
            FROM monthly_aggregation
            ON CONFLICT (month_start, query_id) 
            DO UPDATE SET
                total_clicks = EXCLUDED.total_clicks,
                avg_clicks = EXCLUDED.avg_clicks,
                total_impressions = EXCLUDED.total_impressions,
                avg_impressions = EXCLUDED.avg_impressions,
                avg_position = EXCLUDED.avg_position,
                avg_ctr = EXCLUDED.avg_ctr
        """
        
        try:
            self.cursor.execute(monthly_query, (start_date.date(), end_date.date()))
            self.conn.commit()
            print("Месячная агрегация успешно выполнена")
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при месячной агрегации: {str(e)}")
            raise

    def calculate_average_metrics(self, query_id: int, days: int = 30) -> Dict[str, float]:
        """
        Расчет средних показателей за период
        Args:
            query_id: ID поискового запроса
            days: Количество дней для расчета
        Returns:
            Dict с средними показателями
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = """
            SELECT 
                AVG(position) as avg_position,
                AVG(clicks) as avg_clicks,
                AVG(impressions) as avg_impressions,
                AVG(ctr) as avg_ctr,
                STDDEV(position) as position_std,
                STDDEV(clicks) as clicks_std,
                STDDEV(impressions) as impressions_std,
                STDDEV(ctr) as ctr_std
            FROM daily_metrics
            WHERE query_id = %s
            AND date BETWEEN %s AND %s
        """
        
        self.cursor.execute(query, (query_id, start_date.date(), end_date.date()))
        result = self.cursor.fetchone()

        return {
            'avg_position': float(result['avg_position'] or 0),
            'avg_clicks': float(result['avg_clicks'] or 0),
            'avg_impressions': float(result['avg_impressions'] or 0),
            'avg_ctr': float(result['avg_ctr'] or 0),
            'position_std': float(result['position_std'] or 0),
            'clicks_std': float(result['clicks_std'] or 0),
            'impressions_std': float(result['impressions_std'] or 0),
            'ctr_std': float(result['ctr_std'] or 0)
        }

    def detect_trends(self, query_id: int, days: int = 90) -> Dict[str, Any]:
        """
        Выявление трендов в метриках
        Args:
            query_id: ID поискового запроса
            days: Количество дней для анализа
        Returns:
            Dict с трендами по каждой метрике
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = """
            SELECT 
                date,
                position,
                clicks,
                impressions,
                ctr
            FROM daily_metrics
            WHERE query_id = %s
            AND date BETWEEN %s AND %s
            ORDER BY date
        """
        
        self.cursor.execute(query, (query_id, start_date.date(), end_date.date()))
        data = pd.DataFrame(self.cursor.fetchall())
        
        if data.empty:
            return {}

        trends = {}
        for metric in ['position', 'clicks', 'impressions', 'ctr']:
            if metric in data.columns:
                # Линейная регрессия
                x = np.arange(len(data))
                y = data[metric].values
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                # Определение тренда
                trend_direction = 'neutral'
                if p_value < 0.05:  # Статистически значимый тренд
                    trend_direction = 'positive' if slope < 0 else 'negative' if slope > 0 else 'neutral'
                    if metric == 'position':  # Инвертируем для позиций (меньше = лучше)
                        trend_direction = 'positive' if slope > 0 else 'negative' if slope < 0 else 'neutral'
                
                trends[metric] = {
                    'direction': trend_direction,
                    'slope': slope,
                    'p_value': p_value,
                    'r_squared': r_value ** 2,
                    'significance': 'significant' if p_value < 0.05 else 'not significant'
                }
        
        return trends

    def get_version_info(self) -> Dict[str, Any]:
        """
        Получение информации о версиях данных
        Returns:
            Dict с информацией о версиях
        """
        query = """
            SELECT 
                MAX(date) as last_update,
                COUNT(DISTINCT query_id) as total_queries,
                COUNT(*) as total_records
            FROM daily_metrics
        """
        
        self.cursor.execute(query)
        return self.cursor.fetchone()
