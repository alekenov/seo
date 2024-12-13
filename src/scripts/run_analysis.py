"""
Скрипт для запуска анализа позиций с правильными путями к модулям.
"""
import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

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
    
    try:
        # Запускаем анализ
        print("Запускаем анализ позиций...")
        results = analyzer.analyze_positions(
            days=[1, 7, 30, 60],  # Анализируем за разные периоды
            min_change=3.0,  # Минимальное значимое изменение
        )
        
        print("\nАнализ позиций завершен!")
        print("-" * 50)
        
        # Выводим статистику по каждому периоду
        for period, stats in results['stats'].items():
            print(f"\nПериод: {period} дней")
            print(f"Средняя позиция: {stats.avg_position:.2f}")
            print(f"Улучшилось запросов: {stats.improved_count}")
            print(f"Ухудшилось запросов: {stats.declined_count}")
            print(f"Всего значимых изменений: {stats.significant_changes}")
        
        # Выводим топ изменений за последний день
        if 1 in results['changes']:
            print("\nТоп изменений за последний день:")
            for change in sorted(
                results['changes'][1],
                key=lambda x: abs(x.change),
                reverse=True
            )[:5]:
                print(
                    f"- {change.query} ({change.city or 'все города'}): "
                    f"{change.old_position:.1f} → {change.new_position:.1f} "
                    f"({change.change:+.1f})"
                )
                if change.impressions_change != 0:
                    print(f"  Изменение показов: {change.impressions_change:+d}")
                if change.clicks_change != 0:
                    print(f"  Изменение кликов: {change.clicks_change:+d}")
    
    except Exception as e:
        print(f"Ошибка при анализе: {e}")
        raise

if __name__ == "__main__":
    main()
