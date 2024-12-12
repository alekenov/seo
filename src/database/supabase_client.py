"""Supabase client for database operations."""

import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional

from supabase import create_client, Client
from src.config.supabase_config import SUPABASE_URL, SUPABASE_ANON_KEY

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Client for interacting with Supabase database."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
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
        """
        try:
            # First ensure all queries exist
            for metric in metrics:
                query_data = {
                    'query': metric['query'],
                    'city_id': self._get_city_id(metric.get('city'))
                }
                query_id = self._get_or_create_query(query_data)
                
                # Prepare daily metric data
                daily_data = {
                    'date': metric['date'],
                    'query_id': query_id,
                    'clicks': metric['clicks'],
                    'impressions': metric['impressions'],
                    'position': metric['position'],
                    'ctr': metric['ctr'],
                    'url': metric.get('url')
                }
                
                # Insert daily metrics
                self.client.table('daily_metrics').upsert(
                    daily_data, 
                    on_conflict='date,query_id'
                ).execute()
                
            logger.info(f"Successfully inserted {len(metrics)} daily metrics")
            
        except Exception as e:
            logger.error(f"Error inserting daily metrics: {e}")
            raise
    
    def _get_city_id(self, city_name: Optional[str]) -> Optional[int]:
        """Get city ID from database, create if doesn't exist."""
        if not city_name:
            return None
            
        try:
            result = self.client.table('cities').select('id').eq('name', city_name).execute()
            
            if result.data:
                return result.data[0]['id']
            
            # Create new city if doesn't exist
            result = self.client.table('cities').insert({'name': city_name}).execute()
            return result.data[0]['id']
            
        except Exception as e:
            logger.error(f"Error getting/creating city {city_name}: {e}")
            raise
    
    def _get_or_create_query(self, query_data: Dict[str, Any]) -> int:
        """Get query ID from database, create if doesn't exist."""
        try:
            result = self.client.table('search_queries').select('id').eq(
                'query', query_data['query']
            ).eq('city_id', query_data['city_id']).execute()
            
            if result.data:
                return result.data[0]['id']
            
            # Create new query if doesn't exist
            result = self.client.table('search_queries').insert(query_data).execute()
            return result.data[0]['id']
            
        except Exception as e:
            logger.error(f"Error getting/creating query {query_data}: {e}")
            raise
    
    def get_metrics_by_date_range(
        self, 
        start_date: date,
        end_date: date,
        city_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get metrics for specified date range."""
        try:
            query = self.client.table('daily_metrics').select(
                'daily_metrics.date',
                'search_queries.query',
                'cities.name as city',
                'daily_metrics.clicks',
                'daily_metrics.impressions',
                'daily_metrics.position',
                'daily_metrics.ctr',
                'daily_metrics.url'
            ).join(
                'search_queries',
                'daily_metrics.query_id=search_queries.id'
            ).join(
                'cities',
                'search_queries.city_id=cities.id'
            ).gte('date', start_date).lte('date', end_date)
            
            if city_name:
                query = query.eq('cities.name', city_name)
            
            result = query.execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Error getting metrics for date range: {e}")
            raise
    
    def create_tokens_table(self) -> None:
        """Create tokens table if it doesn't exist."""
        try:
            # SQL для создания таблицы
            sql = """
            CREATE TABLE IF NOT EXISTS tokens (
                id SERIAL PRIMARY KEY,
                service VARCHAR(50) NOT NULL,
                token_data JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(service)
            );
            """
            
            # Выполняем SQL
            self.client.rpc('create_tokens_table', {}).execute()
            logger.info("Tokens table created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tokens table: {e}")
            raise
