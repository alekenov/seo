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
                    ALTER TABLE search_queries
                    ADD COLUMN IF NOT EXISTS clicks integer DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS impressions integer DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS ctr double precision DEFAULT 0.0,
                    ADD COLUMN IF NOT EXISTS position double precision DEFAULT 0.0,
                    ADD COLUMN IF NOT EXISTS date_collected date;
                    
                    -- Add unique constraint
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_constraint 
                            WHERE conname = 'search_queries_query_date_key'
                        ) THEN
                            ALTER TABLE search_queries 
                            ADD CONSTRAINT search_queries_query_date_key 
                            UNIQUE (query, date_collected);
                        END IF;
                    END $$;
                """)
                
                # Update daily_metrics table
                logger.info("Updating daily_metrics table...")
                cur.execute("""
                    ALTER TABLE daily_metrics
                    ADD COLUMN IF NOT EXISTS total_clicks integer DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS total_impressions integer DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS avg_position double precision DEFAULT 0.0;
                    
                    -- Add unique constraint on date
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_constraint 
                            WHERE conname = 'daily_metrics_date_key'
                        ) THEN
                            ALTER TABLE daily_metrics 
                            ADD CONSTRAINT daily_metrics_date_key 
                            UNIQUE (date);
                        END IF;
                    END $$;
                """)
                
                # Update position_changes table
                logger.info("Updating position_changes table...")
                cur.execute("""
                    ALTER TABLE position_changes
                    ADD COLUMN IF NOT EXISTS query text,
                    ADD COLUMN IF NOT EXISTS date_checked date;
                    
                    -- Add unique constraint
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_constraint 
                            WHERE conname = 'position_changes_query_date_key'
                        ) THEN
                            ALTER TABLE position_changes 
                            ADD CONSTRAINT position_changes_query_date_key 
                            UNIQUE (query, date_checked);
                        END IF;
                    END $$;
                """)
                
        logger.info("Successfully updated table structure")
        
    except Exception as e:
        logger.error(f"Error updating table structure: {str(e)}")
        raise

if __name__ == "__main__":
    update_structure()
