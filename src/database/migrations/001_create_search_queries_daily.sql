-- Создаем таблицу для хранения ежедневной статистики
CREATE TABLE IF NOT EXISTS search_queries_daily (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    query TEXT NOT NULL,
    query_type TEXT,
    clicks INTEGER NOT NULL,
    impressions INTEGER NOT NULL,
    position FLOAT NOT NULL,
    ctr FLOAT NOT NULL,
    city TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Индексы для быстрого поиска
    CONSTRAINT unique_query_date_city UNIQUE (date, query, city)
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_search_queries_daily_date ON search_queries_daily(date);
CREATE INDEX IF NOT EXISTS idx_search_queries_daily_query ON search_queries_daily(query);
CREATE INDEX IF NOT EXISTS idx_search_queries_daily_city ON search_queries_daily(city);
CREATE INDEX IF NOT EXISTS idx_search_queries_daily_query_type ON search_queries_daily(query_type);
