-- Create enum types
CREATE TYPE query_type AS ENUM (
    'delivery',     -- доставка цветов
    'flowers',      -- цветы
    'bouquets',     -- букеты
    'gifts',        -- подарки
    'other'         -- другое
);

-- Create cities table
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create search_queries table
CREATE TABLE search_queries (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    query_type query_type,
    city_id INTEGER REFERENCES cities(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(query, city_id)
);

-- Create daily_metrics table
CREATE TABLE daily_metrics (
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

-- Create weekly_metrics table for aggregated data
CREATE TABLE weekly_metrics (
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

-- Create monthly_metrics table for aggregated data
CREATE TABLE monthly_metrics (
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

-- Create position_changes table for tracking significant changes
CREATE TABLE position_changes (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES search_queries(id),
    date DATE NOT NULL,
    old_position FLOAT NOT NULL,
    new_position FLOAT NOT NULL,
    change_percent FLOAT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create anomalies table for tracking unusual patterns
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES search_queries(id),
    date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- clicks, impressions, position, ctr
    expected_value FLOAT NOT NULL,
    actual_value FLOAT NOT NULL,
    deviation_percent FLOAT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_search_queries_city ON search_queries(city_id);
CREATE INDEX idx_daily_metrics_date ON daily_metrics(date);
CREATE INDEX idx_daily_metrics_query ON daily_metrics(query_id);
CREATE INDEX idx_weekly_metrics_date ON weekly_metrics(week_start);
CREATE INDEX idx_monthly_metrics_date ON monthly_metrics(month_start);
CREATE INDEX idx_position_changes_date ON position_changes(date);
CREATE INDEX idx_anomalies_date ON anomalies(date);

-- Functions for automatic updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
CREATE TRIGGER update_cities_updated_at
    BEFORE UPDATE ON cities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
