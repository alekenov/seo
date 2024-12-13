-- Добавляем поле url в таблицу search_queries
ALTER TABLE search_queries ADD COLUMN IF NOT EXISTS url TEXT;
