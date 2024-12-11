"""PostgreSQL client for database operations."""

import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import execute_values
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class PostgresClient:
    """Client for interacting with PostgreSQL database."""
    
    def __init__(
        self,
        host: str = "aws-0-eu-central-1.pooler.supabase.com",
        port: int = 6543,
        database: str = "postgres",
        user: str = "postgres.jvfjxlpplbyrafasobzl",
        password: str = "fogdif-7voHxi-ryfqug"
    ):
        """Initialize PostgreSQL client.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager."""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def insert_daily_metrics(self, metrics: List[Dict[str, Any]]) -> None:
        """Insert daily metrics into database.
        
        Args:
            metrics: List of metric dictionaries containing:
                - date: Date of metrics
                - query: Search query
                - clicks: Number of clicks
                - impressions: Number of impressions
                - position: Average position
                - ctr: Click-through rate
                - url: Target URL
                - city: Optional city name
        """
        if not metrics:
            logger.warning("No metrics to insert")
            return
            
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # First ensure all cities exist
                city_ids = {}
                for metric in metrics:
                    if 'city' in metric and metric['city']:
                        city_name = metric['city']
                        if city_name not in city_ids:
                            cur.execute("""
                                INSERT INTO cities (name)
                                VALUES (%s)
                                ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                                RETURNING id
                            """, (city_name,))
                            result = cur.fetchone()
                            if result:
                                city_ids[city_name] = result[0]
                
                # Then ensure all queries exist
                query_data = []
                query_map = {}  # Map to store (query, city_id) -> index
                for i, metric in enumerate(metrics):
                    city_id = city_ids.get(metric.get('city'))
                    query_data.append((
                        metric['query'],
                        city_id
                    ))
                    query_map[(metric['query'], city_id)] = i
                
                if query_data:
                    execute_values(cur, """
                        INSERT INTO search_queries (query, city_id)
                        VALUES %s
                        ON CONFLICT (query, COALESCE(city_id, -1))
                        DO UPDATE SET query = EXCLUDED.query
                        RETURNING id, query, city_id
                    """, query_data)
                    
                    query_results = cur.fetchall()
                    query_ids = {}
                    for row in query_results:
                        query_ids[(row[1], row[2])] = row[0]
                
                    # Finally insert metrics
                    metric_data = []
                    for metric in metrics:
                        city_id = city_ids.get(metric.get('city'))
                        query_id = query_ids.get((metric['query'], city_id))
                        
                        if query_id:
                            metric_data.append((
                                metric['date'],
                                query_id,
                                metric['clicks'],
                                metric['impressions'],
                                metric['position'],
                                metric['ctr'],
                                metric.get('url')
                            ))
                    
                    if metric_data:
                        execute_values(cur, """
                            INSERT INTO daily_metrics (
                                date, query_id, clicks, impressions,
                                position, ctr, url
                            )
                            VALUES %s
                            ON CONFLICT (date, query_id)
                            DO UPDATE SET
                                clicks = EXCLUDED.clicks,
                                impressions = EXCLUDED.impressions,
                                position = EXCLUDED.position,
                                ctr = EXCLUDED.ctr,
                                url = EXCLUDED.url
                        """, metric_data)
    
    def get_metrics_by_date_range(
        self,
        start_date: date,
        end_date: date,
        city_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get metrics for specified date range.
        
        Args:
            start_date: Start date
            end_date: End date
            city_name: Optional city name to filter by
            
        Returns:
            List of metric dictionaries
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT 
                        dm.date,
                        sq.query,
                        c.name as city,
                        dm.clicks,
                        dm.impressions,
                        dm.position,
                        dm.ctr,
                        dm.url
                    FROM daily_metrics dm
                    JOIN search_queries sq ON dm.query_id = sq.id
                    LEFT JOIN cities c ON sq.city_id = c.id
                    WHERE dm.date BETWEEN %s AND %s
                """
                params = [start_date, end_date]
                
                if city_name:
                    query += " AND c.name = %s"
                    params.append(city_name)
                
                cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
