-- Добавляем date_collected в search_queries если его нет
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'search_queries' 
        AND column_name = 'date_collected'
    ) THEN
        ALTER TABLE search_queries ADD COLUMN date_collected date DEFAULT CURRENT_DATE;
    END IF;
END $$;

-- Создаем уникальный индекс
DROP INDEX IF EXISTS search_queries_query_city_date_idx;
CREATE UNIQUE INDEX search_queries_query_city_date_idx ON search_queries (query, COALESCE(city_id, -1), date_collected);

-- Добавляем индекс для daily_metrics
DROP INDEX IF EXISTS daily_metrics_date_url_idx;
CREATE UNIQUE INDEX daily_metrics_date_url_idx ON daily_metrics (date, url);
