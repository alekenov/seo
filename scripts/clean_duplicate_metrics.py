"""Clean duplicate metrics from database."""

import logging
from src.database.postgres_client import PostgresClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_duplicates():
    """Clean duplicate metrics."""
    try:
        db = PostgresClient()
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Clean daily_metrics duplicates
                logger.info("Cleaning daily_metrics duplicates...")
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
                
                # Clean search_queries duplicates
                logger.info("Cleaning search_queries duplicates...")
                cur.execute("""
                    -- Create temporary table with unique records
                    CREATE TEMP TABLE temp_search_queries AS
                    SELECT DISTINCT ON (query, date_collected) *
                    FROM search_queries
                    ORDER BY query, date_collected, id DESC;
                    
                    -- Delete all records from original table
                    TRUNCATE search_queries;
                    
                    -- Insert unique records back
                    INSERT INTO search_queries
                    SELECT * FROM temp_search_queries;
                    
                    -- Drop temporary table
                    DROP TABLE temp_search_queries;
                """)
                
                # Clean position_changes duplicates
                logger.info("Cleaning position_changes duplicates...")
                cur.execute("""
                    -- Create temporary table with unique records
                    CREATE TEMP TABLE temp_position_changes AS
                    SELECT DISTINCT ON (query, date_checked) *
                    FROM position_changes
                    ORDER BY query, date_checked, id DESC;
                    
                    -- Delete all records from original table
                    TRUNCATE position_changes;
                    
                    -- Insert unique records back
                    INSERT INTO position_changes
                    SELECT * FROM temp_position_changes;
                    
                    -- Drop temporary table
                    DROP TABLE temp_position_changes;
                """)
                
        logger.info("Successfully cleaned duplicate metrics")
        
    except Exception as e:
        logger.error(f"Error cleaning duplicates: {str(e)}")
        raise

if __name__ == "__main__":
    clean_duplicates()
