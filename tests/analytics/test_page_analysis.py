"""
Тесты для модуля анализа страниц.
"""
import pytest
from datetime import datetime, timedelta
from src.analytics.page_analysis import PageAnalyzer

class TestPageAnalyzer:
    @pytest.fixture
    def analyzer(self, mocker):
        # Мокаем клиент базы данных
        mock_db = mocker.Mock()
        return PageAnalyzer(mock_db)
        
    def test_analyze_growth_potential(self, analyzer):
        # Тестовые метрики
        metrics = {
            'traffic': {
                'clicks': 100,
                'impressions': 1000,
                'ctr': 0.01
            },
            'visibility': {
                'avg_position': 15,
                'query_count': 50
            },
            'conversions': {
                'count': 0,
                'value': 0
            }
        }
        
        potential = analyzer._analyze_growth_potential('test.com', metrics)
        
        # Проверяем наличие потенциала
        assert potential['traffic_potential'] > 0
        # Проверяем приоритетные области
        assert len(potential['priority_areas']) > 0
        # Проверяем описания
        assert all('description' in area for area in potential['priority_areas'])
        
    def test_find_page_problems(self, analyzer):
        # Тестовые метрики с проблемами
        metrics = {
            'traffic': {
                'clicks': 5,
                'impressions': 1000,
                'ctr': 0.005
            },
            'visibility': {
                'avg_position': 150,
                'query_count': 10
            },
            'conversions': {
                'count': 0,
                'value': 0
            }
        }
        
        problems = analyzer._find_page_problems(metrics)
        
        # Проверяем наличие проблем
        assert len(problems) > 0
        # Проверяем типы проблем
        problem_types = [p['type'] for p in problems]
        assert 'low_traffic' in problem_types
        assert 'low_ctr' in problem_types
        assert 'poor_visibility' in problem_types
        
    def test_generate_recommendations(self, analyzer):
        # Тестовые проблемы
        problems = [
            {
                'type': 'low_traffic',
                'severity': 'high',
                'description': 'Очень низкий трафик'
            },
            {
                'type': 'low_ctr',
                'severity': 'high',
                'description': 'Критически низкий CTR'
            }
        ]
        
        # Тестовый потенциал роста
        growth_potential = {
            'traffic_potential': 80,
            'conversion_potential': 50,
            'priority_areas': [
                {
                    'area': 'positions',
                    'description': 'Улучшение позиций',
                    'impact': 'высокий'
                }
            ]
        }
        
        recommendations = analyzer._generate_recommendations(problems, growth_potential)
        
        # Проверяем наличие рекомендаций
        assert len(recommendations) > 0
        # Проверяем приоритеты
        assert any(r['priority'] == 'high' for r in recommendations)
        # Проверяем наличие описаний и ожидаемого эффекта
        assert all('description' in r and 'expected_impact' in r 
                  for r in recommendations)
