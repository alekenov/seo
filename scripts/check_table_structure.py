"""Check database table structure."""

import logging
from src.database.postgres_client import PostgresClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_structure():
    """Check table structure."""
    try:
        db = PostgresClient()
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get search_queries table structure
                cur.execute("""
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = 'search_queries'
                    ORDER BY ordinal_position;
                """)
                
                columns = cur.fetchall()
                logger.info("\nSearch Queries table structure:")
                for col in columns:
                    logger.info(f"Column: {col[0]}, Type: {col[1]}, Max Length: {col[2]}")
                
                # Get daily_metrics table structure
                cur.execute("""
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = 'daily_metrics'
                    ORDER BY ordinal_position;
                """)
                
                columns = cur.fetchall()
                logger.info("\nDaily Metrics table structure:")
                for col in columns:
                    logger.info(f"Column: {col[0]}, Type: {col[1]}, Max Length: {col[2]}")
                
                # Get position_changes table structure
                cur.execute("""
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = 'position_changes'
                    ORDER BY ordinal_position;
                """)
                
                columns = cur.fetchall()
                logger.info("\nPosition Changes table structure:")
                for col in columns:
                    logger.info(f"Column: {col[0]}, Type: {col[1]}, Max Length: {col[2]}")
                
    except Exception as e:
        logger.error(f"Error checking table structure: {str(e)}")
        raise

if __name__ == "__main__":
    check_structure()
