-- Drop duplicate constraint
ALTER TABLE search_queries DROP CONSTRAINT IF EXISTS search_queries_query_city_unique;

-- Add updated_at column if missing
ALTER TABLE search_queries ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Add updated_at column to daily_metrics if missing
ALTER TABLE daily_metrics ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
