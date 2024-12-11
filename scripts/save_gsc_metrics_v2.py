"""Script to save GSC metrics to database."""

import logging
from datetime import datetime, timedelta
from src.collectors.gsc_collector import GSCCollector
from src.database.postgres_client import PostgresClient
from psycopg2.extras import execute_values

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_metrics():
    """Save GSC metrics to database."""
    try:
        # Initialize collectors
        gsc = GSCCollector(site_url='sc-domain:cvety.kz')
        db = PostgresClient()
        
        # Get date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        logger.info("Collecting search queries...")
        queries_data = gsc.get_search_queries(start_date, end_date)
        
        if not queries_data:
            logger.warning("No search queries data collected")
            return
            
        logger.info(f"Saving {len(queries_data)} search queries...")
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # First, get existing queries
                cur.execute("""
                    SELECT query, city_id
                    FROM search_queries
                    WHERE query = ANY(%s)
                """, ([q['query'] for q in queries_data],))
                
                existing_queries = {(row[0], row[1]) for row in cur.fetchall()}
                
                # Prepare values for insert/update
                values = []
                for row in queries_data:
                    query = row['query']
                    city_id = None  # We'll implement city detection later
                    
                    if (query, city_id) in existing_queries:
                        # Update existing record
                        cur.execute("""
                            UPDATE search_queries
                            SET 
                                clicks = %s,
                                impressions = %s,
                                ctr = %s,
                                position = %s,
                                date_collected = %s
                            WHERE query = %s AND COALESCE(city_id, -1) = %s
                        """, (
                            row['clicks'],
                            row['impressions'],
                            row['ctr'],
                            row['position'],
                            end_date,
                            query,
                            city_id or -1
                        ))
                    else:
                        # Insert new record
                        values.append((
                            query,
                            city_id,
                            row['clicks'],
                            row['impressions'],
                            row['ctr'],
                            row['position'],
                            end_date
                        ))
                
                if values:
                    insert_query = """
                        INSERT INTO search_queries (
                            query,
                            city_id,
                            clicks,
                            impressions,
                            ctr,
                            position,
                            date_collected
                        )
                        VALUES %s
                    """
                    execute_values(cur, insert_query, values)
                
                conn.commit()
                
        logger.info("Successfully saved search queries")
        
        # TODO: Add logic for saving daily_metrics and position_changes
        
    except Exception as e:
        logger.error(f"Error saving metrics: {str(e)}")
        raise

if __name__ == "__main__":
    save_metrics()
