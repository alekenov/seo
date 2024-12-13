"""
Скрипт для анализа позиций с использованием улучшенного анализатора.
"""
import json
from datetime import datetime
from src.analytics.position_analyzer import EnhancedPositionAnalyzer
from src.database.postgres_client import PostgresClient
from src.config.config import get_config

def format_changes(changes):
    """Форматирование изменений для вывода."""
    return [
        {
            'query': change.query,
            'url': change.url,
            'city': change.city,
            'old_position': round(change.old_position, 1),
            'new_position': round(change.new_position, 1),
            'change': round(change.change, 1),
            'impressions_change': change.impressions_change,
            'clicks_change': change.clicks_change,
            'query_type': change.query_type
        }
        for change in changes
    ]

def format_stats(stats):
    """Форматирование статистики для вывода."""
    return {
        period: {
            'period_days': stat.period_days,
            'avg_position': round(stat.avg_position, 2),
            'improved_count': stat.improved_count,
            'declined_count': stat.declined_count,
            'total_queries': stat.total_queries,
            'significant_changes': stat.significant_changes
        }
        for period, stat in stats.items()
    }

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
        days=[1, 7, 30, 60],  # Анализируем за разные периоды
        min_change=3.0,  # Минимальное значимое изменение
    )
    
    # Форматируем результаты для вывода
    formatted_results = {
        'changes': {
            period: format_changes(changes)
            for period, changes in results['changes'].items()
        },
        'stats': format_stats(results['stats']),
        'summary': results['summary']
    }
    
    # Сохраняем результаты в JSON
    output_file = f"position_analysis_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_results, f, ensure_ascii=False, indent=2)
    
    # Выводим краткую сводку
    print("\nАнализ позиций завершен!")
    print("-" * 50)
    
    # Выводим статистику по каждому периоду
    for period, stats in formatted_results['stats'].items():
        print(f"\nПериод: {period} дней")
        print(f"Средняя позиция: {stats['avg_position']}")
        print(f"Улучшилось запросов: {stats['improved_count']}")
        print(f"Ухудшилось запросов: {stats['declined_count']}")
        print(f"Всего значимых изменений: {stats['significant_changes']}")
    
    # Выводим топ изменений за последний день
    if formatted_results['changes'].get(1):
        print("\nТоп изменений за последний день:")
        for change in sorted(
            formatted_results['changes'][1],
            key=lambda x: abs(x['change']),
            reverse=True
        )[:5]:
            print(
                f"- {change['query']}: "
                f"{change['old_position']:.1f} → {change['new_position']:.1f} "
                f"({change['change']:+.1f})"
            )
    
    print(f"\nРезультаты сохранены в {output_file}")

if __name__ == "__main__":
    main()
