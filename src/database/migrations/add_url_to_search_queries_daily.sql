-- Добавляем поле page_url в таблицу search_queries_daily
ALTER TABLE search_queries_daily ADD COLUMN IF NOT EXISTS page_url TEXT;

-- Создаем индекс для быстрого поиска по URL
CREATE INDEX IF NOT EXISTS idx_search_queries_daily_page_url ON search_queries_daily(page_url);

-- Обновляем ограничение уникальности
ALTER TABLE search_queries_daily 
    DROP CONSTRAINT IF EXISTS unique_query_date_city,
    ADD CONSTRAINT unique_query_date_city_url UNIQUE (date, query, city, page_url);
