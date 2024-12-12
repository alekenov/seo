"""
Тесты для модуля анализа CTR.
"""
import pytest
from datetime import datetime, timedelta
import pandas as pd
from src.analytics.ctr_analysis import CTRAnalyzer

class TestCTRAnalyzer:
    @pytest.fixture
    def analyzer(self, mocker):
        # Мокаем клиент базы данных
        mock_db = mocker.Mock()
        return CTRAnalyzer(mock_db)
        
    def test_is_unstable_ctr(self, analyzer):
        # Тест на нестабильный CTR
        unstable = pd.Series([0.01, 0.1, 0.02, 0.15, 0.01])
        assert analyzer._is_unstable_ctr(unstable)
        
        # Тест на стабильный CTR
        stable = pd.Series([0.05, 0.06, 0.05, 0.04, 0.05])
        assert not analyzer._is_unstable_ctr(stable)
        
    def test_find_ctr_anomalies(self, analyzer):
        # Создаем тестовые данные
        data = {
            'position': [1, 1, 1, 2, 2, 2],
            'clicks': [10, 5, 2, 5, 2, 1],
            'impressions': [100, 100, 100, 100, 100, 100],
            'date': [datetime.now() - timedelta(days=i) for i in range(6)]
        }
        df = pd.DataFrame(data)
        df['ctr'] = df['clicks'] / df['impressions']
        
        anomalies = analyzer._find_ctr_anomalies(df)
        
        # Проверяем, что аномалии найдены
        assert len(anomalies) > 0
        # Проверяем, что аномалии отсортированы по важности
        impacts = [a['impact'] for a in anomalies]
        assert impacts == sorted(impacts, reverse=True)
        
    def test_generate_recommendations(self, analyzer):
        # Создаем тестовые аномалии
        anomalies = [
            {
                'position': 1,
                'actual_ctr': 0.05,
                'expected_ctr': 0.25,
                'type': 'low_ctr',
                'impact': 100
            },
            {
                'position': 2,
                'type': 'unstable_ctr',
                'impact': 50
            }
        ]
        
        df = pd.DataFrame()  # Пустой DataFrame для теста
        recommendations = analyzer._generate_recommendations(df, anomalies)
        
        # Проверяем наличие рекомендаций
        assert len(recommendations) > 0
        # Проверяем приоритеты
        assert any(r['priority'] == 'high' for r in recommendations)
        # Проверяем типы рекомендаций
        assert any(r['type'] == 'title_optimization' for r in recommendations)
