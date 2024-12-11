"""Show examples of collected data."""

import os
import logging
import psycopg2
from tabulate import tabulate
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_data_examples():
    """Show examples of collected data."""
    try:
        # Database connection parameters
        conn_params = {
            'host': "aws-0-eu-central-1.pooler.supabase.com",
            'port': 6543,
            'database': "postgres",
            'user': "postgres.jvfjxlpplbyrafasobzl",
            'password': "fogdif-7voHxi-ryfqug"
        }
        
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        # 1. Show top queries by clicks
        logger.info("\nTop 10 queries by clicks:")
        cur.execute("""
            SELECT 
                sq.query,
                c.name as city,
                SUM(dm.clicks) as total_clicks,
                ROUND(AVG(dm.position)::numeric, 2) as avg_position,
                ROUND(AVG(dm.ctr)::numeric, 4) as avg_ctr
            FROM daily_metrics dm
            JOIN search_queries sq ON dm.query_id = sq.id
            LEFT JOIN cities c ON sq.city_id = c.id
            GROUP BY sq.query, c.name
            ORDER BY total_clicks DESC
            LIMIT 10
        """)
        results = cur.fetchall()
        print(tabulate(results, headers=['Query', 'City', 'Clicks', 'Avg Position', 'Avg CTR'], 
                      tablefmt='psql'))
        
        # 2. Show top pages by impressions
        logger.info("\nTop 10 pages by impressions:")
        cur.execute("""
            SELECT 
                dm.url,
                SUM(dm.impressions) as total_impressions,
                SUM(dm.clicks) as total_clicks,
                ROUND(AVG(dm.position)::numeric, 2) as avg_position
            FROM daily_metrics dm
            WHERE dm.url IS NOT NULL
            GROUP BY dm.url
            ORDER BY total_impressions DESC
            LIMIT 10
        """)
        results = cur.fetchall()
        print(tabulate(results, headers=['URL', 'Impressions', 'Clicks', 'Avg Position'], 
                      tablefmt='psql'))
        
        # 3. Show queries with best positions
        logger.info("\nTop 10 queries by position (lowest is better):")
        cur.execute("""
            SELECT 
                sq.query,
                c.name as city,
                ROUND(AVG(dm.position)::numeric, 2) as avg_position,
                SUM(dm.clicks) as total_clicks,
                SUM(dm.impressions) as total_impressions
            FROM daily_metrics dm
            JOIN search_queries sq ON dm.query_id = sq.id
            LEFT JOIN cities c ON sq.city_id = c.id
            GROUP BY sq.query, c.name
            HAVING SUM(dm.impressions) > 100
            ORDER BY avg_position ASC
            LIMIT 10
        """)
        results = cur.fetchall()
        print(tabulate(results, 
                      headers=['Query', 'City', 'Avg Position', 'Clicks', 'Impressions'], 
                      tablefmt='psql'))
        
        # 4. Show recent metrics
        logger.info("\nMost recent metrics (last 5 days):")
        cur.execute("""
            SELECT 
                dm.date,
                sq.query,
                dm.clicks,
                dm.impressions,
                dm.position,
                ROUND(dm.ctr::numeric, 4) as ctr
            FROM daily_metrics dm
            JOIN search_queries sq ON dm.query_id = sq.id
            WHERE dm.date >= CURRENT_DATE - INTERVAL '5 days'
            ORDER BY dm.date DESC, dm.clicks DESC
            LIMIT 10
        """)
        results = cur.fetchall()
        print(tabulate(results, 
                      headers=['Date', 'Query', 'Clicks', 'Impressions', 'Position', 'CTR'], 
                      tablefmt='psql'))
        
    except Exception as e:
        logger.error(f"Error showing data examples: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    show_data_examples()
