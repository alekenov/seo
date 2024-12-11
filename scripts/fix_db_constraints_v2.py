"""Fix database constraints version 2."""

import os
import logging
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_db_constraints():
    """Fix database constraints."""
    try:
        # Database connection parameters
        conn_params = {
            'host': "aws-0-eu-central-1.pooler.supabase.com",
            'port': 6543,
            'database': "postgres",
            'user': "postgres.jvfjxlpplbyrafasobzl",
            'password': "fogdif-7voHxi-ryfqug"
        }
        
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        # Read SQL file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file = os.path.join(script_dir, 'fix_db_constraints_v2.sql')
        
        with open(sql_file, 'r') as f:
            sql = f.read()
        
        # Execute SQL
        cur.execute(sql)
        
        # Commit changes
        conn.commit()
        logger.info("Database constraints fixed successfully")
        
    except Exception as e:
        logger.error(f"Error fixing database constraints: {e}")
        if conn:
            conn.rollback()
        raise
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_db_constraints()
