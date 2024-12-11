"""Save GSC metrics to database."""

import logging
from datetime import datetime, timedelta
from src.collectors.gsc_collector import GSCCollector
from src.database.postgres_client import PostgresClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_metrics():
    """Collect and save GSC metrics to database."""
    try:
        # Initialize collector and database
        site_url = "sc-domain:cvety.kz"
        collector = GSCCollector(site_url=site_url)
        db = PostgresClient()
        
        # Set date range
        end_date = datetime(2024, 12, 11)  # Today
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        # Get metrics
        logger.info("Collecting search queries...")
        queries = collector.get_search_queries(start_date, end_date)
        
        # Save search queries
        if queries:
            logger.info(f"Saving {len(queries)} search queries...")
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Insert queries
                    insert_query = """
                        INSERT INTO search_queries 
                        (query, clicks, impressions, ctr, position, date_collected)
                        VALUES %s
                        ON CONFLICT (query, date_collected) 
                        DO UPDATE SET
                            clicks = EXCLUDED.clicks,
                            impressions = EXCLUDED.impressions,
                            ctr = EXCLUDED.ctr,
                            position = EXCLUDED.position;
                    """
                    
                    # Prepare data
                    values = [
                        (
                            q.get('query'),
                            q.get('clicks', 0),
                            q.get('impressions', 0),
                            q.get('ctr', 0.0),
                            q.get('position', 0.0),
                            end_date.date()
                        )
                        for q in queries
                    ]
                    
                    # Execute insert
                    from psycopg2.extras import execute_values
                    execute_values(cur, insert_query, values)
            
            logger.info("Successfully saved search queries")
        
        # Save daily metrics
        logger.info("Saving daily metrics...")
        total_clicks = sum(q.get('clicks', 0) for q in queries)
        total_impressions = sum(q.get('impressions', 0) for q in queries)
        avg_position = sum(q.get('position', 0) * q.get('impressions', 0) 
                         for q in queries) / total_impressions if total_impressions > 0 else 0
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                insert_query = """
                    INSERT INTO daily_metrics 
                    (date, total_clicks, total_impressions, avg_position)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (date) 
                    DO UPDATE SET
                        total_clicks = EXCLUDED.total_clicks,
                        total_impressions = EXCLUDED.total_impressions,
                        avg_position = EXCLUDED.avg_position;
                """
                
                cur.execute(insert_query, (
                    end_date.date(),
                    total_clicks,
                    total_impressions,
                    avg_position
                ))
        
        logger.info("Successfully saved daily metrics")
        
        # Save position changes for top queries
        logger.info("Saving position changes...")
        position_metrics = collector.get_position_metrics(start_date, end_date)
        if position_metrics:
            # Get top 100 queries by impressions
            sorted_metrics = sorted(
                position_metrics, 
                key=lambda x: x.get('impressions', 0), 
                reverse=True
            )[:100]
            
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    insert_query = """
                        INSERT INTO position_changes 
                        (query, old_position, new_position, date_checked)
                        VALUES %s
                        ON CONFLICT (query, date_checked) 
                        DO UPDATE SET
                            old_position = EXCLUDED.old_position,
                            new_position = EXCLUDED.new_position;
                    """
                    
                    values = [
                        (
                            m.get('query'),
                            0.0,  # We don't have old position yet
                            m.get('position', 0.0),
                            end_date.date()
                        )
                        for m in sorted_metrics
                    ]
                    
                    execute_values(cur, insert_query, values)
            
            logger.info("Successfully saved position changes")
        
    except Exception as e:
        logger.error(f"Error saving metrics: {str(e)}")
        raise

if __name__ == "__main__":
    save_metrics()
