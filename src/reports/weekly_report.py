"""
Модуль для генерации еженедельных отчетов.
Включает в себя сбор данных, форматирование и отправку отчетов.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.utils.credentials_manager import CredentialsManager
from src.database.supabase_client import SupabaseClient
from src.services.gsc_service import GSCService
from src.services.telegram_service import TelegramService
from src.reports.constants import TOP_LIMITS


class WeeklyReport:
    """Класс для генерации и отправки еженедельных отчетов."""
    
    def __init__(self):
        """Инициализация объекта WeeklyReport."""
        self.credentials = CredentialsManager()
        self.db = SupabaseClient()
        self.gsc = GSCService()
        self.telegram = TelegramService()
        
    def get_date_range(self) -> tuple[datetime, datetime]:
        """Получает диапазон дат для отчета (последние 7 дней)."""
        end_date = datetime.now() - timedelta(days=3)  # GSC данные отстают на 3 дня
        start_date = end_date - timedelta(days=7)
        return start_date, end_date
        
    def collect_metrics(self) -> Dict:
        """
        Собирает основные метрики для отчета.
        
        Returns:
            Dict: Словарь с метриками по категориям
        """
        start_date, end_date = self.get_date_range()
        
        # Получаем данные из GSC
        analytics_data = self.gsc.get_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=['page', 'query']
        )
        
        # Группируем данные по категориям
        categories = self.gsc.group_by_category(analytics_data)
        
        # Получаем топ запросы
        top_queries = self.gsc.get_top_queries(
            analytics_data,
            limit=TOP_LIMITS['queries']
        )
        
        # Собираем общие метрики
        total_impressions = sum(row['impressions'] for row in analytics_data.get('rows', []))
        total_clicks = sum(row['clicks'] for row in analytics_data.get('rows', []))
        
        # Считаем среднюю позицию
        weighted_position = sum(
            row['position'] * row['impressions']
            for row in analytics_data.get('rows', [])
        )
        avg_position = weighted_position / total_impressions if total_impressions > 0 else 0
        
        return {
            'overall': {
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'avg_position': avg_position,
                'top_queries': [q['query'] for q in top_queries],
                'top_pages': []  # TODO: Добавить топ страниц
            },
            'categories': categories
        }
        
    def format_report(self, metrics: Dict) -> str:
        """
        Форматирует отчет для отправки в Telegram.
        
        Args:
            metrics: Словарь с метриками
            
        Returns:
            str: Отформатированный текст отчета
        """
        start_date, end_date = self.get_date_range()
        
        report = [
            f"📊 Еженедельный отчет по SEO",
            f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n",
            "📈 Общие показатели:",
            f"• Показы: {metrics['overall']['total_impressions']:,}",
            f"• Клики: {metrics['overall']['total_clicks']:,}",
            f"• Средняя позиция: {metrics['overall']['avg_position']:.1f}\n",
            "🔝 Топ запросы:",
        ]
        
        # Добавляем топ запросы
        for query in metrics['overall']['top_queries'][:5]:
            report.append(f"• {query}")
            
        report.append("\n📱 По категориям:")
        # Добавляем метрики по категориям
        for category, data in metrics['categories'].items():
            report.append(f"\n{category}:")
            report.append(f"• Показы: {data['impressions']:,}")
            report.append(f"• Клики: {data['clicks']:,}")
            report.append(f"• CTR: {data['ctr']:.1%}")
            
        return "\n".join(report)
        
    def send_report(self, report_text: str) -> bool:
        """
        Отправляет отчет в Telegram канал.
        
        Args:
            report_text: Текст отчета
            
        Returns:
            bool: True если отчет успешно отправлен
        """
        try:
            # Добавляем форматирование
            formatted_text = (
                f"<b>{report_text}</b>\n\n"
                f"<i>Отчет сгенерирован {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>"
            )
            
            # Отправляем отчет
            return self.telegram.send_message_sync(formatted_text)
        except Exception as e:
            print(f"Ошибка при отправке отчета: {e}")
            return False

    def generate_and_send(self) -> bool:
        """
        Генерирует и отправляет еженедельный отчет.
        
        Returns:
            bool: True если отчет успешно сгенерирован и отправлен
        """
        try:
            metrics = self.collect_metrics()
            report = self.format_report(metrics)
            return self.send_report(report)
        except Exception as e:
            print(f"Ошибка при генерации отчета: {e}")
            return False
