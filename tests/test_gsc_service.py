"""Тесты для GSC сервиса."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.services.gsc_service import GSCService


class TestGSCService(unittest.TestCase):
    """Тесты для класса GSCService."""
    
    def setUp(self):
        """Подготовка к тестам."""
        self.gsc = GSCService()
        
    def test_get_page_category(self):
        """Тест определения категории страницы."""
        test_cases = [
            ('/product/123', 'Товары'),
            ('/category/flowers', 'Категории'),
            ('/blog/post-1', 'Блог'),
            ('/about', 'Прочее'),
            ('/', 'Прочее')
        ]
        
        for url, expected in test_cases:
            category = self.gsc.get_page_category(url)
            self.assertEqual(category, expected)
            
    @patch('src.services.gsc_service.build')
    def test_get_search_analytics(self, mock_build):
        """Тест получения данных из Search Analytics."""
        # Подготавливаем мок-данные
        mock_response = {
            'rows': [
                {
                    'keys': ['/product/123', 'розы'],
                    'clicks': 100,
                    'impressions': 1000,
                    'ctr': 0.1,
                    'position': 2.5
                }
            ]
        }
        
        # Настраиваем мок
        mock_service = Mock()
        mock_service.searchanalytics().query().execute.return_value = mock_response
        mock_build.return_value = mock_service
        
        # Вызываем тестируемый метод
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        result = self.gsc.get_search_analytics(start_date, end_date)
        
        # Проверяем результат
        self.assertEqual(result, mock_response)
        
    def test_group_by_category(self):
        """Тест группировки данных по категориям."""
        test_data = {
            'rows': [
                {
                    'keys': ['/product/123', 'query1'],
                    'clicks': 100,
                    'impressions': 1000,
                    'position': 2.5
                },
                {
                    'keys': ['/blog/post-1', 'query2'],
                    'clicks': 50,
                    'impressions': 500,
                    'position': 3.5
                }
            ]
        }
        
        result = self.gsc.group_by_category(test_data)
        
        # Проверяем наличие всех категорий
        self.assertIn('Товары', result)
        self.assertIn('Блог', result)
        
        # Проверяем метрики для категории "Товары"
        self.assertEqual(result['Товары']['clicks'], 100)
        self.assertEqual(result['Товары']['impressions'], 1000)
        
        # Проверяем метрики для категории "Блог"
        self.assertEqual(result['Блог']['clicks'], 50)
        self.assertEqual(result['Блог']['impressions'], 500)
        
    def test_get_top_queries(self):
        """Тест получения топ запросов."""
        test_data = {
            'rows': [
                {
                    'keys': ['/page1', 'query1'],
                    'clicks': 100,
                    'impressions': 1000,
                    'position': 2.5
                },
                {
                    'keys': ['/page2', 'query2'],
                    'clicks': 50,
                    'impressions': 500,
                    'position': 3.5
                }
            ]
        }
        
        result = self.gsc.get_top_queries(test_data, limit=2)
        
        # Проверяем количество запросов
        self.assertEqual(len(result), 2)
        
        # Проверяем сортировку по кликам
        self.assertEqual(result[0]['clicks'], 100)
        self.assertEqual(result[1]['clicks'], 50)
        
        # Проверяем расчет CTR
        self.assertEqual(result[0]['ctr'], 0.1)


if __name__ == '__main__':
    unittest.main()
