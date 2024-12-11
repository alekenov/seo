"""Check database indexes and constraints."""

import logging
from src.database.postgres_client import PostgresClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_indexes():
    """Check table indexes and constraints."""
    try:
        db = PostgresClient()
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get all indexes
                cur.execute("""
                    SELECT
                        schemaname,
                        tablename,
                        indexname,
                        indexdef
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                    ORDER BY tablename, indexname;
                """)
                
                indexes = cur.fetchall()
                
                current_table = None
                for idx in indexes:
                    if current_table != idx[1]:
                        current_table = idx[1]
                        logger.info(f"\nTable: {current_table}")
                    
                    logger.info(f"Index: {idx[2]}")
                    logger.info(f"Definition: {idx[3]}")
                
    except Exception as e:
        logger.error(f"Error checking indexes: {str(e)}")
        raise

if __name__ == "__main__":
    check_indexes()
