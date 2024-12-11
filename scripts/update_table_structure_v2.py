"""Update database table structure."""

import logging
from src.database.postgres_client import PostgresClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_structure():
    """Update table structure."""
    try:
        db = PostgresClient()
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Update search_queries table
                logger.info("Updating search_queries table...")
                cur.execute("""
                    -- Add new columns
                    ALTER TABLE search_queries
                    ADD COLUMN IF NOT EXISTS clicks integer DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS impressions integer DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS ctr double precision DEFAULT 0.0,
                    ADD COLUMN IF NOT EXISTS position double precision DEFAULT 0.0,
                    ADD COLUMN IF NOT EXISTS date_collected date;
                """)
                
                # Update daily_metrics table
                logger.info("Updating daily_metrics table...")
                cur.execute("""
                    -- Add new columns
                    ALTER TABLE daily_metrics
                    ADD COLUMN IF NOT EXISTS total_clicks integer DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS total_impressions integer DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS avg_position double precision DEFAULT 0.0;
                """)
                
                # Update position_changes table
                logger.info("Updating position_changes table...")
                cur.execute("""
                    -- Add new columns
                    ALTER TABLE position_changes
                    ADD COLUMN IF NOT EXISTS query text,
                    ADD COLUMN IF NOT EXISTS date_checked date;
                """)
                
                # Clean duplicates
                logger.info("Cleaning duplicates...")
                
                # Clean daily_metrics
                cur.execute("""
                    -- Create temporary table with unique records
                    CREATE TEMP TABLE temp_daily_metrics AS
                    SELECT DISTINCT ON (date) *
                    FROM daily_metrics
                    ORDER BY date, id DESC;
                    
                    -- Delete all records from original table
                    TRUNCATE daily_metrics;
                    
                    -- Insert unique records back
                    INSERT INTO daily_metrics
                    SELECT * FROM temp_daily_metrics;
                    
                    -- Drop temporary table
                    DROP TABLE temp_daily_metrics;
                """)
                
                # Add unique constraints
                logger.info("Adding unique constraints...")
                cur.execute("""
                    -- Add unique constraints
                    ALTER TABLE search_queries 
                    ADD CONSTRAINT IF NOT EXISTS search_queries_query_date_key 
                    UNIQUE (query, date_collected);
                    
                    ALTER TABLE daily_metrics 
                    ADD CONSTRAINT IF NOT EXISTS daily_metrics_date_key 
                    UNIQUE (date);
                    
                    ALTER TABLE position_changes 
                    ADD CONSTRAINT IF NOT EXISTS position_changes_query_date_key 
                    UNIQUE (query, date_checked);
                """)
                
        logger.info("Successfully updated table structure")
        
    except Exception as e:
        logger.error(f"Error updating table structure: {str(e)}")
        raise

if __name__ == "__main__":
    update_structure()
