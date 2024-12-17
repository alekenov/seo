"""
Модуль для генерации еженедельных отчетов.
Включает в себя сбор данных, форматирование и отправку отчетов.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

from src.utils.credentials_manager import CredentialsManager
from src.database.supabase_client import SupabaseClient
from src.services.gsc_service import GSCService
from src.services.telegram_service import TelegramService
from src.reports.constants import TOP_LIMITS
from src.reports.visualizer import ReportVisualizer

class WeeklyReport:
    """Класс для генерации и отправки еженедельных отчетов."""
    
    def __init__(self):
        """Инициализация объекта WeeklyReport."""
        self.credentials = CredentialsManager()
        self.db = SupabaseClient()
        self.gsc = GSCService()
        self.telegram = TelegramService()
        self.visualizer = ReportVisualizer()
        
    def get_date_range(self) -> tuple[datetime, datetime, datetime, datetime]:
        """
        Получает диапазон дат для текущей и предыдущей недели.
        
        Returns:
            tuple: (начало текущей недели, конец текущей недели, 
                   начало предыдущей недели, конец предыдущей недели)
        """
        end_date = datetime.now() - timedelta(days=3)  # GSC данные отстают на 3 дня
        start_date = end_date - timedelta(days=7)
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = prev_end_date - timedelta(days=7)
        return start_date, end_date, prev_start_date, prev_end_date
        
    def get_comparison_data(self) -> Dict:
        """
        Получает сравнительные данные за текущую и предыдущую неделю.
        
        Returns:
            Dict: Словарь с метриками и их изменениями
        """
        start_date, end_date, prev_start, prev_end = self.get_date_range()
        
        # Выполняем запрос через Supabase
        result = self.db.client.table('search_queries_daily').select('*').execute()
        data = result.data
        
        # Фильтруем данные по датам
        current_week_data = [
            row for row in data 
            if start_date <= datetime.fromisoformat(row['date']) <= end_date
        ]
        
        previous_week_data = [
            row for row in data 
            if prev_start <= datetime.fromisoformat(row['date']) <= prev_end
        ]
        
        # Группируем данные
        categories = {}
        cities = {}
        queries = []
        
        # Обрабатываем текущую неделю
        for row in current_week_data:
            query = row['query']
            query_type = row['query_type']
            city = row['city']
            
            # Находим соответствующие данные за предыдущую неделю
            prev_data = next(
                (r for r in previous_week_data 
                 if r['query'] == query 
                 and r['query_type'] == query_type 
                 and r['city'] == city),
                None
            )
            
            # Добавляем в список запросов
            query_data = {
                'query': query,
                'current_clicks': row['clicks'],
                'previous_clicks': prev_data['clicks'] if prev_data else 0,
                'current_position': row['position'],
                'previous_position': prev_data['position'] if prev_data else 0,
            }
            
            # Вычисляем изменения
            query_data['clicks_change'] = (
                ((query_data['current_clicks'] - query_data['previous_clicks']) / 
                 query_data['previous_clicks'] * 100)
                if query_data['previous_clicks'] > 0 else 
                (100 if query_data['current_clicks'] > 0 else 0)
            )
            
            query_data['position_change'] = (
                query_data['previous_position'] - query_data['current_position']
            )
            
            queries.append(query_data)
            
            # Группируем по категориям
            if query_type not in categories:
                categories[query_type] = {
                    'current_clicks': 0,
                    'previous_clicks': 0,
                    'current_impressions': 0,
                    'previous_impressions': 0
                }
            cat = categories[query_type]
            cat['current_clicks'] += row['clicks']
            cat['current_impressions'] += row['impressions']
            if prev_data:
                cat['previous_clicks'] += prev_data['clicks']
                cat['previous_impressions'] += prev_data['impressions']
            
            # Группируем по городам
            if city and city not in cities:
                cities[city] = {
                    'current_clicks': 0,
                    'previous_clicks': 0,
                    'current_impressions': 0,
                    'previous_impressions': 0
                }
            if city:
                city_data = cities[city]
                city_data['current_clicks'] += row['clicks']
                city_data['current_impressions'] += row['impressions']
                if prev_data:
                    city_data['previous_clicks'] += prev_data['clicks']
                    city_data['previous_impressions'] += prev_data['impressions']
        
        # Сортируем запросы по изменению кликов
        queries.sort(key=lambda x: abs(x['clicks_change']), reverse=True)
        
        return {
            'queries': queries[:TOP_LIMITS['queries']],
            'categories': categories,
            'cities': cities
        }
        
    def format_comparison_report(self, data: Dict) -> tuple[str, List[bytes]]:
        """
        Форматирует отчет со сравнением метрик.
        
        Args:
            data: Словарь с метриками и изменениями
            
        Returns:
            tuple[str, List[bytes]]: Отформатированный текст отчета и список изображений
        """
        start_date, end_date, prev_start, prev_end = self.get_date_range()
        
        report = [
            f"📊 Еженедельный отчет по SEO",
            f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n",
            "🔄 Сравнение с предыдущей неделей:\n"
        ]
        
        # Создаем список для хранения изображений
        images = []
        
        # Добавляем график изменения позиций
        position_chart = self.visualizer.create_position_changes(
            data['queries'],
            "Изменение позиций по топ запросам"
        )
        images.append(position_chart)
        
        # Добавляем график по категориям
        category_chart = self.visualizer.create_category_comparison(
            data['categories'],
            'clicks',
            "Сравнение кликов по категориям"
        )
        images.append(category_chart)
        
        # Добавляем растущие запросы
        report.append("📈 РАСТУЩИЕ ЗАПРОСЫ:")
        growing_queries = sorted(
            [q for q in data['queries'] if q['clicks_change'] > 0],
            key=lambda x: x['clicks_change'],
            reverse=True
        )[:5]
        
        for q in growing_queries:
            report.extend([
                f"• {q['query']}",
                f"  Клики: {q['current_clicks']} (+{q['clicks_change']:.1f}%)",
                f"  Позиция: {q['current_position']:.1f} ({'+' if q['position_change'] > 0 else ''}{q['position_change']:.1f})"
            ])
        
        # Добавляем падающие запросы
        report.append("\n📉 ПАДАЮЩИЕ ЗАПРОСЫ:")
        declining_queries = sorted(
            [q for q in data['queries'] if q['clicks_change'] < 0],
            key=lambda x: x['clicks_change']
        )[:5]
        
        for q in declining_queries:
            report.extend([
                f"• {q['query']}",
                f"  Клики: {q['current_clicks']} ({q['clicks_change']:.1f}%)",
                f"  Позиция: {q['current_position']:.1f} ({'+' if q['position_change'] > 0 else ''}{q['position_change']:.1f})"
            ])
        
        # Добавляем статистику по категориям
        report.append("\n📊 ПО КАТЕГОРИЯМ:")
        for cat_name, cat_data in data['categories'].items():
            clicks_change = ((cat_data['current_clicks'] - cat_data['previous_clicks']) / 
                           cat_data['previous_clicks'] * 100 if cat_data['previous_clicks'] else 0)
            report.extend([
                f"• {cat_name}:",
                f"  Клики: {cat_data['current_clicks']} ({'+' if clicks_change > 0 else ''}{clicks_change:.1f}%)"
            ])
            
        # Добавляем рекомендации
        report.extend(self._generate_recommendations(data))
        
        return "\n".join(report), images
        
    def _generate_recommendations(self, data: Dict) -> List[str]:
        """
        Генерирует рекомендации на основе анализа данных.
        
        Args:
            data: Словарь с метриками и изменениями
            
        Returns:
            List[str]: Список рекомендаций
        """
        recommendations = ["\n📋 РЕКОМЕНДАЦИИ:"]
        
        # Анализируем падающие запросы
        declining_queries = [
            q for q in data['queries'] 
            if q['clicks_change'] < -20 or q['position_change'] < -3
        ]
        
        if declining_queries:
            recommendations.append("1. Обратить внимание на запросы с падением:")
            for q in declining_queries[:3]:
                recommendations.append(
                    f"   • {q['query']} - проверить контент и оптимизацию"
                )
                
        # Анализируем категории
        problematic_categories = []
        for cat_name, cat_data in data['categories'].items():
            clicks_change = ((cat_data['current_clicks'] - cat_data['previous_clicks']) / 
                           cat_data['previous_clicks'] * 100 if cat_data['previous_clicks'] else 0)
            if clicks_change < -15:
                problematic_categories.append((cat_name, clicks_change))
                
        if problematic_categories:
            recommendations.append("\n2. Проблемные категории:")
            for cat_name, change in problematic_categories:
                recommendations.append(
                    f"   • {cat_name} (падение {change:.1f}%) - "
                    "проверить основные посадочные страницы"
                )
                
        # Добавляем общие рекомендации
        if len(recommendations) > 1:  # если есть конкретные проблемы
            recommendations.append(
                "\n3. Общие рекомендации:"
                "\n   • Проверить техническое состояние проблемных страниц"
                "\n   • Обновить контент на страницах с падением позиций"
                "\n   • Проанализировать контент конкурентов по проблемным запросам"
            )
        else:
            recommendations.extend([
                "1. Продолжать работу над контентом для растущих запросов",
                "2. Регулярно обновлять информацию на ключевых страницах",
                "3. Отслеживать активность конкурентов в топе"
            ])
            
        return recommendations
        
    def send_weekly_report(self) -> bool:
        """
        Формирует и отправляет еженедельный отчет.
        
        Returns:
            bool: True если отчет успешно отправлен, False в противном случае
        """
        try:
            # Получаем данные для отчета
            data = self.get_comparison_data()
            
            # Форматируем отчет и получаем графики
            report_text, images = self.format_comparison_report(data)
            
            # Отправляем текст отчета
            self.telegram.send_message(report_text)
            
            # Отправляем графики
            for image in images:
                self.telegram.send_photo(image)
                
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при отправке еженедельного отчета: {str(e)}")
            return False
