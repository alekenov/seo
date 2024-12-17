from src.analytics.position_analyzer import EnhancedPositionAnalyzer
from src.database.postgres_client import PostgresClient
from tabulate import tabulate
from datetime import date

def main():
    # Инициализируем анализатор
    analyzer = EnhancedPositionAnalyzer(PostgresClient())
    
    # Анализируем позиции между 11 декабря 2023 и 6 декабря 2024
    start_date = date(2023, 12, 11)
    end_date = date(2024, 12, 6)
    
    changes, stats = analyzer.get_position_changes(
        start_date=start_date,
        end_date=end_date,
        min_change=0.5  # Уменьшаем порог для теста
    )
    
    # Выводим статистику
    print("\nСтатистика изменений:")
    print(f"Всего запросов: {stats.total_queries}")
    print(f"Значимых изменений: {stats.significant_changes}")
    print(f"Улучшений: {stats.improved_count}")
    print(f"Ухудшений: {stats.declined_count}")
    print(f"Средняя позиция: {stats.avg_position:.2f}")
    
    # Выводим топ изменений
    if changes:
        print("\nТоп изменений позиций:")
        table_data = []
        for change in sorted(changes, key=lambda x: abs(x.change), reverse=True)[:10]:
            table_data.append([
                change.query[:30],  # Обрезаем длинные запросы
                change.city or 'все города',
                f"{change.old_position:.1f}",
                f"{change.new_position:.1f}",
                f"{change.change:+.1f}",
                change.impressions_change,
                change.clicks_change,
                change.query_type
            ])
        
        print(tabulate(
            table_data,
            headers=["Запрос", "Город", "Старая", "Новая", "Изменение", "Показы Δ", "Клики Δ", "Тип"],
            tablefmt="grid"
        ))
    else:
        print("\nЗначимых изменений не найдено")

if __name__ == "__main__":
    main()
