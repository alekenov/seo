"""Check database structure."""

import os
import logging
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_db_structure():
    """Check database structure."""
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
        
        # Get list of tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        
        logger.info("Tables in database:")
        for table in tables:
            table_name = table[0]
            logger.info(f"\nTable: {table_name}")
            
            # Get columns
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = '{table_name}'
            """)
            columns = cur.fetchall()
            logger.info("Columns:")
            for col in columns:
                logger.info(f"  {col[0]}: {col[1]} (Nullable: {col[2]})")
            
            # Get constraints
            cur.execute(f"""
                SELECT con.conname, con.contype,
                    pg_get_constraintdef(con.oid)
                FROM pg_constraint con
                JOIN pg_namespace nsp ON nsp.oid = con.connamespace
                JOIN pg_class cls ON cls.oid = con.conrelid
                WHERE cls.relname = '{table_name}'
                AND nsp.nspname = 'public'
            """)
            constraints = cur.fetchall()
            logger.info("Constraints:")
            for con in constraints:
                logger.info(f"  {con[0]} ({con[1]}): {con[2]}")
            
            logger.info("-" * 50)
            
    except Exception as e:
        logger.error(f"Error checking database structure: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    check_db_structure()
