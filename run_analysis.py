import sys
import os

# Добавляем путь к проекту в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analytics.live_analysis import LiveAnalyzer

if __name__ == '__main__':
    analyzer = LiveAnalyzer()
    analyzer.analyze_live_data(days=30)
