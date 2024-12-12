"""
Скрипт для анализа позиций с использованием улучшенного анализатора.
"""
import json
from datetime import datetime
from src.analytics.position_analyzer import EnhancedPositionAnalyzer
from src.database.postgres_client import PostgresClient
from src.config.config import get_config

def main():
    # Загружаем конфигурацию
    config = get_config()
    
    # Инициализируем клиент БД
    db_client = PostgresClient(
        host=config['database']['host'],
        port=config['database']['port'],
        database=config['database']['name'],
        user=config['database']['user'],
        password=config['database']['password']
    )
    
    # Создаем анализатор
    analyzer = EnhancedPositionAnalyzer(db_client)
    
    # Запускаем анализ
    results = analyzer.analyze_positions(
        days=30,  # Анализируем за 30 дней
        min_change=3.0,  # Минимальное значимое изменение
    )
    
    # Сохраняем результаты в JSON
    output_file = f"position_analysis_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Выводим краткую сводку
    print("\nАнализ позиций завершен!")
    print("-" * 50)
    print(f"Всего запросов: {results['summary']['total_queries']}")
    print(f"Всего URL: {results['summary']['total_urls']}")
    print(f"Средняя позиция: {results['summary']['avg_position']:.2f}")
    print("\nИзменения за 7 дней:")
    print(f"Улучшилось: {results['period_comparison']['improved_7d']}")
    print(f"Ухудшилось: {results['period_comparison']['declined_7d']}")
    print("\nТоп улучшения:")
    for change in results['significant_changes']['improved'][:5]:
        print(f"- {change.query}: {change.old_position:.1f} → {change.new_position:.1f}")
    print("\nПроблемные URL:")
    for url in results['trends']['problematic_urls'][:5]:
        print(f"- {url}")
    print(f"\nРезультаты сохранены в {output_file}")

if __name__ == "__main__":
    main()
