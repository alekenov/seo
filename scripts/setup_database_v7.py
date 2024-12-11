"""Setup database schema."""

import os
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Setup database schema."""
    # Database connection parameters
    conn_params = {
        'host': "aws-0-eu-central-1.pooler.supabase.com",
        'port': 6543,
        'database': "postgres",
        'user': "postgres.jvfjxlpplbyrafasobzl",
        'password': "fogdif-7voHxi-ryfqug"
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        # Read SQL file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file = os.path.join(script_dir, 'setup_database.sql')
        
        with open(sql_file, 'r') as f:
            sql = f.read()
        
        # Execute SQL
        cur.execute(sql)
        
        # Commit changes
        conn.commit()
        logger.info("Database setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        if conn:
            conn.rollback()
        raise
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_database()
