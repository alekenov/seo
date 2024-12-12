import sys
import os

# Добавляем путь к проекту в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analytics.live_analysis import LiveAnalyzer
from src.analytics.position_analyzer import EnhancedPositionAnalyzer
from src.database.postgres_client import PostgresClient

def analyze_positions():
    """Анализ позиций с использованием улучшенного анализатора."""
    # Используем настройки по умолчанию из PostgresClient
    db_client = PostgresClient()
    
    # Создаем анализатор
    analyzer = EnhancedPositionAnalyzer(db_client)
    
    print("\nЗапуск анализа позиций...")
    results = analyzer.analyze_positions(
        days=30,  # Анализируем за 30 дней
        min_change=3.0,  # Минимальное значимое изменение
    )
    
    # Выводим краткую сводку
    print("\nАнализ позиций завершен!")
    print("-" * 50)
    print(f"Всего запросов: {results['summary']['total_queries']}")
    print(f"Всего URL: {results['summary']['total_urls']}")
    print(f"Средняя позиция: {results['summary']['avg_position']:.2f}")
    print(f"Улучшилось запросов: {results['summary']['improved_queries']}")
    print(f"Ухудшилось запросов: {results['summary']['declined_queries']}")
    print(f"Стабильных запросов: {results['summary']['stable_queries']}")
    
    print("\nИзменения за 7 дней:")
    print(f"Улучшилось: {results['period_comparison']['improved_7d']}")
    print(f"Ухудшилось: {results['period_comparison']['declined_7d']}")
    print(f"Средняя позиция (текущая неделя): {results['period_comparison']['last_7d_avg']:.2f}")
    print(f"Средняя позиция (прошлая неделя): {results['period_comparison']['prev_7d_avg']:.2f}")
    
    print("\nТоп улучшения:")
    for change in results['significant_changes']['improved'][:5]:
        print(f"- {change.query}: {change.old_position:.1f} → {change.new_position:.1f} ({change.significance})")
    
    print("\nТоп ухудшения:")
    for change in results['significant_changes']['declined'][:5]:
        print(f"- {change.query}: {change.old_position:.1f} → {change.new_position:.1f} ({change.significance})")
    
    print("\nПроблемные URL:")
    for url in results['trends']['problematic_urls'][:5]:
        print(f"- {url}")
        
    print("\nАномалии:")
    for anomaly in results['anomalies'][:5]:
        print(f"- {anomaly['query']}: резкое изменение с {anomaly['old_position']:.1f} на {anomaly['new_position']:.1f}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'positions':
        analyze_positions()
    else:
        analyzer = LiveAnalyzer()
        analyzer.analyze_live_data(days=30)
