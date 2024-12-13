"""Тесты для модуля weekly_report."""

import unittest
from datetime import datetime, timedelta
from src.reports.weekly_report import WeeklyReport


class TestWeeklyReport(unittest.TestCase):
    """Тесты для класса WeeklyReport."""
    
    def setUp(self):
        """Подготовка к тестам."""
        self.report = WeeklyReport()
        
    def test_date_range(self):
        """Тест получения диапазона дат."""
        start_date, end_date = self.report.get_date_range()
        
        # Проверяем что разница между датами 7 дней
        self.assertEqual((end_date - start_date).days, 7)
        
        # Проверяем что конечная дата не в будущем
        self.assertLessEqual(end_date, datetime.now())
        
    def test_format_report(self):
        """Тест форматирования отчета."""
        test_metrics = {
            'overall': {
                'total_impressions': 1000,
                'total_clicks': 100,
                'avg_position': 12.5,
                'top_queries': ['query1', 'query2'],
                'top_pages': ['/page1', '/page2']
            },
            'categories': {
                'Категория 1': {
                    'impressions': 500,
                    'clicks': 50,
                    'ctr': 0.1
                }
            }
        }
        
        report_text = self.report.format_report(test_metrics)
        
        # Проверяем наличие основных элементов в отчете
        self.assertIn('Еженедельный отчет', report_text)
        self.assertIn('Общие показатели', report_text)
        self.assertIn('1,000', report_text)  # форматирование чисел
        self.assertIn('12.5', report_text)  # средняя позиция
        self.assertIn('Категория 1', report_text)
        
    def test_empty_metrics(self):
        """Тест обработки пустых метрик."""
        empty_metrics = {
            'overall': {
                'total_impressions': 0,
                'total_clicks': 0,
                'avg_position': 0,
                'top_queries': [],
                'top_pages': []
            },
            'categories': {}
        }
        
        report_text = self.report.format_report(empty_metrics)
        
        # Проверяем что отчет генерируется без ошибок
        self.assertIsInstance(report_text, str)
        self.assertGreater(len(report_text), 0)


if __name__ == '__main__':
    unittest.main()
