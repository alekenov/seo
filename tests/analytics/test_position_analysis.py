"""
Тесты для модуля анализа позиций.
"""
import pytest
from datetime import datetime, timedelta
import pandas as pd
from src.analytics.position_analysis import PositionAnalyzer

class TestPositionAnalyzer:
    @pytest.fixture
    def analyzer(self, mocker):
        # Мокаем клиент базы данных
        mock_db = mocker.Mock()
        return PositionAnalyzer(mock_db)
        
    def test_calculate_trend(self, analyzer):
        # Тест на улучшение позиций
        improving = [10, 8, 6, 4, 2]
        assert analyzer._calculate_trend(improving) < 0
        
        # Тест на ухудшение позиций
        declining = [2, 4, 6, 8, 10]
        assert analyzer._calculate_trend(declining) > 0
        
        # Тест на стабильные позиции
        stable = [5, 5, 5, 5, 5]
        assert abs(analyzer._calculate_trend(stable)) < 0.1
        
    def test_has_sudden_drop(self, analyzer):
        # Тест на резкое падение
        positions = [3, 4, 15, 16]
        assert analyzer._has_sudden_drop(positions)
        
        # Тест без падения
        positions = [3, 4, 5, 6]
        assert not analyzer._has_sudden_drop(positions)
        
    def test_is_unstable(self, analyzer):
        # Тест на нестабильные позиции
        unstable = [1, 10, 2, 9, 3]
        assert analyzer._is_unstable(unstable)
        
        # Тест на стабильные позиции
        stable = [4, 5, 4, 5, 4]
        assert not analyzer._is_unstable(stable)
