"""Script to setup database schema."""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.supabase_config import DATABASE_URL

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_schema():
    """Create database schema."""
    conn = None
    cur = None
    try:
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        logger.info("Connected to database successfully")

        # Create enum types
        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE query_type AS ENUM (
                    'delivery',
                    'flowers',
                    'bouquets',
                    'gifts',
                    'other'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        
        # Create cities table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cities (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                name_en VARCHAR(100),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        # Create search_queries table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS search_queries (
                id SERIAL PRIMARY KEY,
                query TEXT NOT NULL,
                query_type query_type,
                city_id INTEGER REFERENCES cities(id),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(query, city_id)
            );
        """)
        
        # Create daily_metrics table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS daily_metrics (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                query_id INTEGER REFERENCES search_queries(id),
                clicks INTEGER NOT NULL DEFAULT 0,
                impressions INTEGER NOT NULL DEFAULT 0,
                position FLOAT NOT NULL,
                ctr FLOAT NOT NULL,
                url TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(date, query_id)
            );
        """)
        
        # Create weekly_metrics table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS weekly_metrics (
                id SERIAL PRIMARY KEY,
                week_start DATE NOT NULL,
                query_id INTEGER REFERENCES search_queries(id),
                avg_clicks FLOAT NOT NULL,
                total_clicks INTEGER NOT NULL,
                avg_impressions FLOAT NOT NULL,
                total_impressions INTEGER NOT NULL,
                avg_position FLOAT NOT NULL,
                avg_ctr FLOAT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(week_start, query_id)
            );
        """)
        
        # Create monthly_metrics table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS monthly_metrics (
                id SERIAL PRIMARY KEY,
                month_start DATE NOT NULL,
                query_id INTEGER REFERENCES search_queries(id),
                avg_clicks FLOAT NOT NULL,
                total_clicks INTEGER NOT NULL,
                avg_impressions FLOAT NOT NULL,
                total_impressions INTEGER NOT NULL,
                avg_position FLOAT NOT NULL,
                avg_ctr FLOAT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(month_start, query_id)
            );
        """)
        
        # Create position_changes table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS position_changes (
                id SERIAL PRIMARY KEY,
                query_id INTEGER REFERENCES search_queries(id),
                date DATE NOT NULL,
                old_position FLOAT NOT NULL,
                new_position FLOAT NOT NULL,
                change_percent FLOAT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        # Create anomalies table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS anomalies (
                id SERIAL PRIMARY KEY,
                query_id INTEGER REFERENCES search_queries(id),
                date DATE NOT NULL,
                metric_type VARCHAR(50) NOT NULL,
                expected_value FLOAT NOT NULL,
                actual_value FLOAT NOT NULL,
                deviation_percent FLOAT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_queries_city ON search_queries(city_id);
            CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_metrics(date);
            CREATE INDEX IF NOT EXISTS idx_daily_metrics_query ON daily_metrics(query_id);
            CREATE INDEX IF NOT EXISTS idx_weekly_metrics_date ON weekly_metrics(week_start);
            CREATE INDEX IF NOT EXISTS idx_monthly_metrics_date ON monthly_metrics(month_start);
            CREATE INDEX IF NOT EXISTS idx_position_changes_date ON position_changes(date);
            CREATE INDEX IF NOT EXISTS idx_anomalies_date ON anomalies(date);
        """)
        
        # Create updated_at trigger function
        cur.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        # Create trigger
        cur.execute("""
            DROP TRIGGER IF EXISTS update_cities_updated_at ON cities;
            CREATE TRIGGER update_cities_updated_at
                BEFORE UPDATE ON cities
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)
        
        logger.info("Database schema created successfully")
        
    except Exception as e:
        logger.error(f"Error creating database schema: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def main():
    """Main function."""
    create_schema()

if __name__ == "__main__":
    main()
