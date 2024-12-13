"""
Тесты для EnhancedPositionAnalyzer
"""
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from src.analytics.position_analyzer import EnhancedPositionAnalyzer, PositionChange, PeriodStats
from src.database.postgres_client import PostgresClient

class TestEnhancedPositionAnalyzer(unittest.TestCase):
    """Тесты для EnhancedPositionAnalyzer."""
    
    def setUp(self):
        """Подготовка тестового окружения."""
        self.db_client = MagicMock(spec=PostgresClient)
        self.analyzer = EnhancedPositionAnalyzer(self.db_client)
        
        # Тестовые данные для изменений позиций
        self.position_changes_data = [
            {
                'query': 'test query',
                'url': 'https://test.com',
                'city_name': 'Moscow',
                'old_position': 10.0,
                'new_position': 5.0,
                'position_change': 5.0,
                'position_change_abs': 5.0,
                'impressions_change': 100,
                'clicks_change': 10,
                'query_type': 'informational'
            }
        ]
        
        # Тестовые данные для статистики
        self.period_stats_data = [
            {
                'period_days': 30,
                'avg_position': 15.5,
                'improved_count': 10,
                'declined_count': 5,
                'total_queries': 100,
                'significant_changes': 15
            }
        ]
    
    def test_get_position_changes(self):
        """Тест получения изменений позиций."""
        self.db_client.fetch_all.return_value = self.position_changes_data
        
        start_date = datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date()
        
        changes = self.analyzer.get_position_changes(
            start_date=start_date,
            end_date=end_date,
            min_change=3.0
        )
        
        self.assertEqual(len(changes), 1)
        change = changes[0]
        self.assertIsInstance(change, PositionChange)
        self.assertEqual(change.query, 'test query')
        self.assertEqual(change.url, 'https://test.com')
        self.assertEqual(change.city, 'Moscow')
        self.assertEqual(change.old_position, 10.0)
        self.assertEqual(change.new_position, 5.0)
        self.assertEqual(change.change, 5.0)
        self.assertEqual(change.change_abs, 5.0)
        self.assertEqual(change.impressions_change, 100)
        self.assertEqual(change.clicks_change, 10)
        self.assertEqual(change.query_type, 'informational')
        
        # Проверяем вызов SQL функции
        self.db_client.fetch_all.assert_called_once()
        call_args = self.db_client.fetch_all.call_args[0]
        self.assertIn('get_position_changes', call_args[0])
    
    def test_get_period_stats(self):
        """Тест получения статистики по периодам."""
        self.db_client.fetch_all.return_value = self.period_stats_data
        
        current_date = datetime.now().date()
        periods = [30]
        
        stats = self.analyzer.get_period_stats(current_date, periods)
        
        self.assertEqual(len(stats), 1)
        period_stats = stats[30]
        self.assertIsInstance(period_stats, PeriodStats)
        self.assertEqual(period_stats.period_days, 30)
        self.assertEqual(period_stats.avg_position, 15.5)
        self.assertEqual(period_stats.improved_count, 10)
        self.assertEqual(period_stats.declined_count, 5)
        self.assertEqual(period_stats.total_queries, 100)
        self.assertEqual(period_stats.significant_changes, 15)
        
        # Проверяем вызов SQL функции
        self.db_client.fetch_all.assert_called_once()
        call_args = self.db_client.fetch_all.call_args[0]
        self.assertIn('get_position_stats', call_args[0])
    
    def test_analyze_positions(self):
        """Тест комплексного анализа позиций."""
        # Настраиваем моки для обоих методов
        self.db_client.fetch_all.side_effect = [
            self.period_stats_data,  # для get_period_stats
            self.position_changes_data  # для get_position_changes
        ]
        
        result = self.analyzer.analyze_positions(
            days=[30],
            min_change=3.0,
            query_type='informational'
        )
        
        self.assertIn('changes', result)
        self.assertIn('stats', result)
        self.assertIn('summary', result)
        
        # Проверяем изменения
        changes = result['changes'][30]
        self.assertEqual(len(changes), 1)
        self.assertIsInstance(changes[0], PositionChange)
        
        # Проверяем статистику
        stats = result['stats']
        self.assertEqual(len(stats), 1)
        self.assertIsInstance(stats[30], PeriodStats)
        
        # Проверяем сводку
        summary = result['summary']
        self.assertEqual(summary['total_analyzed_periods'], 1)
        self.assertEqual(summary['min_change_threshold'], 3.0)
        self.assertEqual(summary['query_type_filter'], 'informational')

if __name__ == '__main__':
    unittest.main()
