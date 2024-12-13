"""Модуль для анализа поисковых запросов по городам."""
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta

from src.database.postgres_client import PostgresClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class CityAnalyzer:
    """Анализатор поисковых запросов по городам."""
    
    def __init__(self):
        """Инициализация анализатора."""
        self.db = PostgresClient()
            
    def analyze_cities(self, days: int = 30) -> Dict[str, Any]:
        """Анализ запросов по городам.
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Dict с результатами анализа по городам
        """
        logger.info(f"Анализируем данные за последние {days} дней")
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                # Получаем статистику по городам
                query = """
                    WITH city_stats AS (
                        SELECT 
                            CASE 
                                WHEN query_type LIKE '%%almaty%%' THEN 'almaty'
                                WHEN query_type LIKE '%%astana%%' THEN 'astana'
                                WHEN query_type LIKE '%%shymkent%%' THEN 'shymkent'
                                WHEN query_type LIKE '%%karaganda%%' THEN 'karaganda'
                                WHEN query_type LIKE '%%pavlodar%%' THEN 'pavlodar'
                                WHEN query_type LIKE '%%kostanay%%' THEN 'kostanay'
                                ELSE 'other'
                            END as city,
                            COUNT(DISTINCT query) as query_count,
                            COALESCE(SUM(clicks), 0) as total_clicks,
                            COALESCE(SUM(impressions), 0) as total_impressions,
                            COALESCE(AVG(position), 0) as avg_position,
                            COALESCE(AVG(CASE WHEN impressions > 0 THEN clicks::float / impressions ELSE 0 END), 0) as avg_ctr
                        FROM search_queries
                        WHERE date_collected >= CURRENT_DATE - INTERVAL '%s days'
                        GROUP BY 
                            CASE 
                                WHEN query_type LIKE '%%almaty%%' THEN 'almaty'
                                WHEN query_type LIKE '%%astana%%' THEN 'astana'
                                WHEN query_type LIKE '%%shymkent%%' THEN 'shymkent'
                                WHEN query_type LIKE '%%karaganda%%' THEN 'karaganda'
                                WHEN query_type LIKE '%%pavlodar%%' THEN 'pavlodar'
                                WHEN query_type LIKE '%%kostanay%%' THEN 'kostanay'
                                ELSE 'other'
                            END
                    )
                    SELECT 
                        city,
                        query_count,
                        total_clicks,
                        total_impressions,
                        ROUND(avg_position::numeric, 2) as avg_position,
                        ROUND((avg_ctr * 100)::numeric, 2) as ctr_percentage
                    FROM city_stats
                    ORDER BY total_impressions DESC
                """
                
                logger.info("Выполняем SQL запрос:")
                logger.info(query % days)
                
                cur.execute(query, (days,))
                results = cur.fetchall()
                
                logger.info(f"Получено {len(results)} строк")
                
                city_stats = {}
                for i, row in enumerate(results):
                    logger.info(f"Обрабатываем строку {i + 1}: {row}")
                    city_stats[row[0]] = {
                        'query_count': row[1] or 0,
                        'total_clicks': row[2] or 0,
                        'total_impressions': row[3] or 0,
                        'avg_position': row[4] or 0,
                        'ctr_percentage': row[5] or 0
                    }
                    
                return city_stats

    def get_top_queries_by_city(self, city: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение топ запросов по городу.
        
        Args:
            city: Название города
            limit: Количество запросов
            
        Returns:
            Список топ запросов
        """
        logger.info(f"Получаем топ запросы по городу {city} с лимитом {limit}")
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT 
                        query,
                        query_type,
                        COALESCE(SUM(clicks), 0) as total_clicks,
                        COALESCE(SUM(impressions), 0) as total_impressions,
                        COALESCE(AVG(position), 0) as avg_position,
                        COALESCE(AVG(CASE WHEN impressions > 0 THEN clicks::float / impressions ELSE 0 END), 0) * 100 as ctr_percentage
                    FROM search_queries
                    WHERE query_type LIKE '%%' || %s || '%%'
                    GROUP BY query, query_type
                    ORDER BY total_impressions DESC
                    LIMIT %s
                """
                
                logger.info("Выполняем SQL запрос:")
                logger.info(query % (city, limit))
                
                cur.execute(query, (city, limit))
                results = cur.fetchall()
                
                logger.info(f"Получено {len(results)} строк")
                
                queries = []
                for i, row in enumerate(results):
                    logger.info(f"Обрабатываем строку {i + 1}: {row}")
                    queries.append({
                        'query': row[0],
                        'query_type': row[1],
                        'total_clicks': row[2] or 0,
                        'total_impressions': row[3] or 0,
                        'avg_position': round(row[4] or 0, 2),
                        'ctr_percentage': round(row[5] or 0, 2)
                    })
                    
                return queries
