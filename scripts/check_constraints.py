"""Check database constraints."""

import logging
from src.database.postgres_client import PostgresClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_constraints():
    """Check table constraints."""
    try:
        db = PostgresClient()
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get all constraints
                cur.execute("""
                    SELECT
                        tc.table_name, 
                        tc.constraint_name, 
                        tc.constraint_type,
                        kcu.column_name,
                        tc.is_deferrable,
                        tc.initially_deferred
                    FROM 
                        information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu
                          ON tc.constraint_name = kcu.constraint_name
                         AND tc.table_schema = kcu.table_schema
                    WHERE tc.table_schema = 'public'
                    ORDER BY tc.table_name, tc.constraint_name;
                """)
                
                constraints = cur.fetchall()
                
                current_table = None
                for constraint in constraints:
                    if current_table != constraint[0]:
                        current_table = constraint[0]
                        logger.info(f"\nTable: {current_table}")
                    
                    logger.info(
                        f"Constraint: {constraint[1]}, "
                        f"Type: {constraint[2]}, "
                        f"Column: {constraint[3]}"
                    )
                
    except Exception as e:
        logger.error(f"Error checking constraints: {str(e)}")
        raise

if __name__ == "__main__":
    check_constraints()
