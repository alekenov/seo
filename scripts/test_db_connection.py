"""Test database connection."""

import logging
from src.database.postgres_client import PostgresClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test database connection."""
    try:
        # Initialize client
        db = PostgresClient()
        
        # Try to connect and execute simple query
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                logger.info(f"Successfully connected to PostgreSQL. Version: {version[0]}")
                
                # List all tables
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = cur.fetchall()
                logger.info("Available tables:")
                for table in tables:
                    logger.info(f"- {table[0]}")
                
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise

if __name__ == "__main__":
    test_connection()
