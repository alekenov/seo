-- Создаем таблицу городов
CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создаем таблицу поисковых запросов
DROP TABLE IF EXISTS search_queries;
CREATE TABLE search_queries (
    id SERIAL PRIMARY KEY,
    query VARCHAR(255) NOT NULL,
    city_id INTEGER REFERENCES cities(id),
    query_type VARCHAR(50),
    clicks INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    ctr FLOAT DEFAULT 0,
    position FLOAT DEFAULT 0,
    date_collected DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создаем уникальный индекс
CREATE UNIQUE INDEX search_queries_unique_idx ON search_queries (query, COALESCE(city_id, -1), date_collected);

-- Создаем таблицу ежедневных метрик
CREATE TABLE IF NOT EXISTS daily_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    url VARCHAR(255) NOT NULL,
    clicks INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    position FLOAT DEFAULT 0,
    ctr FLOAT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT daily_metrics_unique UNIQUE (date, url)
);
