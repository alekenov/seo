"""Скрипт для тестирования новой системы категоризации."""
import os
import sys
from datetime import datetime, timedelta

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.analytics.city_analyzer import CityAnalyzer
from src.utils.logger import setup_logger
from fetch_search_data import categorize_query

logger = setup_logger(__name__)

def test_categorization():
    """Тестирование категоризации на примерах."""
    test_queries = [
        "доставка цветов алматы",
        "купить розы астана",
        "цветы алматы",
        "букет пионов астана цена",
        "заказать букет алматы",
        "доставка тюльпанов астана",
        "цветы на свадьбу алматы",
        "розы караганда",
        "купить букет шымкент"
    ]
    
    logger.info("Тестирование категоризации запросов:")
    logger.info("-" * 50)
    
    for query in test_queries:
        category = categorize_query(query)
        logger.info(f"Запрос: {query}")
        logger.info(f"Категория: {category}")
        logger.info("-" * 50)

def analyze_cities():
    """Анализ статистики по городам."""
    analyzer = CityAnalyzer()
    
    # Анализ всех городов
    logger.info("\nОбщая статистика по городам:")
    logger.info("=" * 50)
    
    city_stats = analyzer.analyze_cities(days=30)
    for city, stats in city_stats.items():
        logger.info(f"\nГород: {city}")
        logger.info(f"Всего запросов: {stats['query_count']}")
        logger.info(f"Кликов: {stats['total_clicks']}")
        logger.info(f"Показов: {stats['total_impressions']}")
        logger.info(f"Средняя позиция: {stats['avg_position']}")
        logger.info(f"Средний CTR: {stats['ctr_percentage']}%")
        logger.info("-" * 50)
    
    # Детальный анализ Алматы и Астаны
    for city in ['almaty', 'astana']:
        logger.info(f"\nДетальный анализ города {city.upper()}:")
        logger.info("=" * 50)
        
        # Получаем топ запросов для города
        top_queries = analyzer.get_top_queries_by_city(city, limit=10)
        
        logger.info("\nТоп запросы:")
        logger.info("-" * 30)
        
        for query in top_queries:
            logger.info(f"\nЗапрос: {query['query']}")
            logger.info(f"Тип: {query['query_type']}")
            logger.info(f"Кликов: {query['total_clicks']}")
            logger.info(f"Показов: {query['total_impressions']}")
            logger.info(f"Средняя позиция: {query['avg_position']}")
            logger.info(f"CTR: {query['ctr_percentage']}%")

def main():
    """Основная функция."""
    try:
        # Тестируем категоризацию
        test_categorization()
        
        # Анализируем статистику по городам
        analyze_cities()
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}")
        raise

if __name__ == "__main__":
    main()
