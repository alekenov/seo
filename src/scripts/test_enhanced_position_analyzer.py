"""
Скрипт для тестирования улучшенного анализатора позиций.
"""
import os
import sys
from datetime import datetime, timedelta
from tabulate import tabulate

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.analytics.position_analyzer import EnhancedPositionAnalyzer
from src.database.postgres_client import PostgresClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def print_position_changes(changes, stats):
    """Вывод изменений позиций в читаемом формате."""
    # Выводим статистику
    print("\nСтатистика:")
    print(f"Период: {stats.period_days} дней")
    print(f"Средняя позиция: {stats.avg_position:.2f}")
    print(f"Улучшилось: {stats.improved_count}")
    print(f"Ухудшилось: {stats.declined_count}")
    print(f"Всего запросов: {stats.total_queries}")
    print(f"Значимых изменений: {stats.significant_changes}")
    print(f"Сезонных запросов: {stats.seasonality_affected}")
    print(f"С активными конкурентами: {stats.competitors_affected}")
    
    # Выводим изменения позиций
    if changes:
        print("\nТоп-10 изменений позиций:")
        rows = []
        for change in sorted(changes, key=lambda x: abs(x.change), reverse=True)[:10]:
            competitors = ", ".join(change.competitors) if change.competitors else "-"
            rows.append([
                change.query,
                change.url,
                change.city or "-",
                f"{change.old_position:.1f}",
                f"{change.new_position:.1f}",
                f"{change.change:+.1f}",
                "Да" if change.is_seasonal else "Нет",
                f"{change.seasonality_score:.2f}",
                competitors
            ])
        
        headers = [
            "Запрос", 
            "URL", 
            "Город", 
            "Старая поз.", 
            "Новая поз.", 
            "Изменение",
            "Сезонный",
            "Сезонность",
            "Конкуренты"
        ]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        print("\nНет значимых изменений позиций")

def main():
    """Основная функция."""
    try:
        # Инициализируем анализатор
        db = PostgresClient()
        analyzer = EnhancedPositionAnalyzer(db)
        
        # Получаем еженедельные изменения за последний месяц
        end_date = datetime.now()
        weekly_changes = analyzer.get_weekly_changes(
            end_date=end_date,
            weeks_back=4,
            min_change=3.0,
            include_seasonality=True,
            include_competitors=True
        )
        
        # Выводим результаты по неделям
        for week_start, changes, stats in weekly_changes:
            print(f"\n{'='*80}")
            print(f"Неделя {week_start.strftime('%Y-%m-%d')} - {(week_start + timedelta(days=7)).strftime('%Y-%m-%d')}")
            print_position_changes(changes, stats)
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
