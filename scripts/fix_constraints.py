"""Fix database constraints."""

import logging
from src.database.postgres_client import PostgresClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_constraints():
    """Fix table constraints."""
    try:
        db = PostgresClient()
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Drop conflicting constraints
                logger.info("Dropping conflicting constraints...")
                
                # Drop constraints from search_queries
                cur.execute("""
                    ALTER TABLE search_queries
                    DROP CONSTRAINT IF EXISTS search_queries_query_city_id_key,
                    DROP CONSTRAINT IF EXISTS search_queries_query_date_key;
                """)
                
                # Drop constraints from daily_metrics
                cur.execute("""
                    ALTER TABLE daily_metrics
                    DROP CONSTRAINT IF EXISTS daily_metrics_date_query_id_key,
                    DROP CONSTRAINT IF EXISTS daily_metrics_date_key;
                """)
                
                # Drop constraints from position_changes
                cur.execute("""
                    ALTER TABLE position_changes
                    DROP CONSTRAINT IF EXISTS position_changes_query_date_key;
                """)
                
                # Add correct constraints
                logger.info("Adding correct constraints...")
                
                # Add constraint for search_queries
                cur.execute("""
                    ALTER TABLE search_queries 
                    ADD CONSTRAINT search_queries_query_date_collected_key 
                    UNIQUE (query, date_collected);
                """)
                
                # Add constraint for daily_metrics
                cur.execute("""
                    ALTER TABLE daily_metrics 
                    ADD CONSTRAINT daily_metrics_date_key 
                    UNIQUE (date);
                """)
                
                # Add constraint for position_changes
                cur.execute("""
                    ALTER TABLE position_changes 
                    ADD CONSTRAINT position_changes_query_date_key 
                    UNIQUE (query, date_checked);
                """)
                
        logger.info("Successfully fixed constraints")
        
    except Exception as e:
        logger.error(f"Error fixing constraints: {str(e)}")
        raise

if __name__ == "__main__":
    fix_constraints()
