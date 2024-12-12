-- Удаляем существующие таблицы, если они есть
DROP TABLE IF EXISTS daily_metrics CASCADE;
DROP TABLE IF EXISTS search_queries CASCADE;
DROP TABLE IF EXISTS cities CASCADE;

-- Таблица городов
CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT cities_name_unique UNIQUE (name)
);

-- Таблица поисковых запросов
CREATE TABLE IF NOT EXISTS search_queries (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    city_id INTEGER REFERENCES cities(id),
    query_type VARCHAR(50) NOT NULL,
    clicks INTEGER NOT NULL DEFAULT 0,
    impressions INTEGER NOT NULL DEFAULT 0,
    ctr FLOAT NOT NULL DEFAULT 0,
    position FLOAT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_collected DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT search_queries_unique UNIQUE (query, city_id, date_collected)
);

-- Таблица ежедневных метрик
CREATE TABLE IF NOT EXISTS daily_metrics (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES search_queries(id),
    url TEXT NOT NULL,
    clicks INTEGER NOT NULL DEFAULT 0,
    impressions INTEGER NOT NULL DEFAULT 0,
    ctr FLOAT NOT NULL DEFAULT 0,
    position FLOAT NOT NULL DEFAULT 0,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT daily_metrics_unique UNIQUE (query_id, date)
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_search_queries_query_type ON search_queries(query_type);
CREATE INDEX IF NOT EXISTS idx_search_queries_date ON search_queries(date_collected);
CREATE INDEX IF NOT EXISTS idx_search_queries_city ON search_queries(city_id);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_metrics(date);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_query ON daily_metrics(query_id);

-- Функция для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггеры для обновления updated_at
DROP TRIGGER IF EXISTS update_cities_updated_at ON cities;
CREATE TRIGGER update_cities_updated_at
    BEFORE UPDATE ON cities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_search_queries_updated_at ON search_queries;
CREATE TRIGGER update_search_queries_updated_at
    BEFORE UPDATE ON search_queries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
