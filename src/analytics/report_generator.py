"""Генератор отчетов для SEO статистики."""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import pandas as pd

from src.database.postgres_client import PostgresClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ReportGenerator:
    """Генератор отчетов по SEO метрикам."""
    
    def __init__(self):
        """Инициализация генератора отчетов."""
        self.db = PostgresClient()
    
    def generate_daily_report(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Генерация ежедневного отчета.
        
        Args:
            date: Дата отчета (по умолчанию сегодня)
            
        Returns:
            Dict с данными отчета
        """
        if date is None:
            date = datetime.now()
            
        yesterday = date - timedelta(days=1)
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                # Получаем статистику за сегодня и вчера
                cur.execute("""
                    WITH today_stats AS (
                        SELECT 
                            sq.query_type,
                            COUNT(*) as query_count,
                            AVG(sq.position) as avg_position,
                            SUM(sq.clicks) as total_clicks,
                            SUM(sq.impressions) as total_impressions
                        FROM search_queries sq
                        WHERE DATE(sq.date_collected) = %s
                        GROUP BY sq.query_type
                    ),
                    yesterday_stats AS (
                        SELECT 
                            sq.query_type,
                            AVG(sq.position) as yesterday_avg_position
                        FROM search_queries sq
                        WHERE DATE(sq.date_collected) = %s
                        GROUP BY sq.query_type
                    ),
                    position_changes AS (
                        SELECT 
                            sq.query,
                            sq.position as current_pos,
                            ysq.position as prev_pos,
                            (ysq.position - sq.position) as position_change
                        FROM search_queries sq
                        JOIN search_queries ysq ON sq.query = ysq.query 
                            AND DATE(ysq.date_collected) = %s
                        WHERE DATE(sq.date_collected) = %s
                            AND ABS(ysq.position - sq.position) >= 3
                        ORDER BY ABS(ysq.position - sq.position) DESC
                        LIMIT 10
                    )
                    SELECT 
                        json_build_object(
                            'summary', (
                                SELECT json_object_agg(
                                    t.query_type,
                                    json_build_object(
                                        'query_count', t.query_count,
                                        'avg_position', ROUND(t.avg_position::numeric, 2),
                                        'total_clicks', t.total_clicks,
                                        'total_impressions', t.total_impressions,
                                        'position_change', ROUND((t.avg_position - y.yesterday_avg_position)::numeric, 2)
                                    )
                                )
                                FROM today_stats t
                                LEFT JOIN yesterday_stats y USING (query_type)
                            ),
                            'significant_changes', (
                                SELECT json_agg(
                                    json_build_object(
                                        'query', query,
                                        'current_pos', ROUND(current_pos::numeric, 2),
                                        'prev_pos', ROUND(prev_pos::numeric, 2),
                                        'change', ROUND(position_change::numeric, 2)
                                    )
                                )
                                FROM position_changes
                            )
                        ) as report_data
                """, (date.date(), yesterday.date(), yesterday.date(), date.date()))
                
                result = cur.fetchone()
                report_data = result[0] if result else {}
                
                # Добавляем дату в отчет
                report_data['date'] = date.strftime('%Y-%m-%d')
                
                return report_data
    
    def format_report_message(self, report_data: Dict[str, Any]) -> str:
        """Форматирование отчета для отправки в Telegram.
        
        Args:
            report_data: Данные отчета
            
        Returns:
            str: Отформатированное сообщение
        """
        message = f"📊 <b>Отчет по SEO позициям за {report_data.get('date', 'сегодня')}</b>\n\n"
        
        if report_data.get('summary'):
            message += "📈 <b>Сводка по категориям:</b>\n"
            for category, stats in report_data['summary'].items():
                change = stats.get('position_change', 0)
                change_emoji = "🔼" if change < 0 else "🔽" if change > 0 else "➡️"
                
                message += (
                    f"\n<b>{category}</b>\n"
                    f"• Запросов: {stats.get('query_count', 0)}\n"
                    f"• Средняя позиция: {stats.get('avg_position', 0)} {change_emoji} ({abs(change)})\n"
                    f"• Клики: {stats.get('total_clicks', 0)}\n"
                    f"• Показы: {stats.get('total_impressions', 0)}\n"
                )
        else:
            message += "❌ Нет данных за указанный период\n"
        
        if report_data.get('significant_changes'):
            message += "\n🔄 <b>Значимые изменения позиций:</b>\n"
            for change in report_data['significant_changes']:
                change_val = change.get('change', 0)
                change_emoji = "🔼" if change_val > 0 else "🔽"
                message += (
                    f"• {change.get('query', '')}: {change.get('prev_pos', 0)} → {change.get('current_pos', 0)} "
                    f"{change_emoji} ({abs(change_val)})\n"
                )
        
        return message
