"""Script to setup database schema using Supabase client."""

import os
import sys
import logging
from supabase import create_client, Client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.supabase_config import SUPABASE_URL, SUPABASE_SERVICE_ROLE

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_schema():
    """Create database schema using Supabase client."""
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)
        logger.info("Connected to Supabase successfully")

        # Execute schema creation SQL
        schema_sql = """
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

        CREATE TABLE IF NOT EXISTS cities (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            name_en VARCHAR(100),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS search_queries (
            id SERIAL PRIMARY KEY,
            query TEXT NOT NULL,
            query_type query_type,
            city_id INTEGER REFERENCES cities(id),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(query, city_id)
        );

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

        CREATE TABLE IF NOT EXISTS position_changes (
            id SERIAL PRIMARY KEY,
            query_id INTEGER REFERENCES search_queries(id),
            date DATE NOT NULL,
            old_position FLOAT NOT NULL,
            new_position FLOAT NOT NULL,
            change_percent FLOAT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

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

        CREATE INDEX IF NOT EXISTS idx_search_queries_city ON search_queries(city_id);
        CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_metrics(date);
        CREATE INDEX IF NOT EXISTS idx_daily_metrics_query ON daily_metrics(query_id);
        CREATE INDEX IF NOT EXISTS idx_weekly_metrics_date ON weekly_metrics(week_start);
        CREATE INDEX IF NOT EXISTS idx_monthly_metrics_date ON monthly_metrics(month_start);
        CREATE INDEX IF NOT EXISTS idx_position_changes_date ON position_changes(date);
        CREATE INDEX IF NOT EXISTS idx_anomalies_date ON anomalies(date);

        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        DROP TRIGGER IF EXISTS update_cities_updated_at ON cities;
        CREATE TRIGGER update_cities_updated_at
            BEFORE UPDATE ON cities
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """

        # Execute the SQL using Supabase client
        result = supabase.rpc('exec_sql', {'sql': schema_sql}).execute()
        
        logger.info("Database schema created successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error creating database schema: {e}")
        raise

def main():
    """Main function."""
    create_schema()

if __name__ == "__main__":
    main()
