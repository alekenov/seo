-- Удаляем старый индекс если есть
DROP INDEX IF EXISTS search_queries_unique_idx;

-- Создаем новый уникальный индекс
CREATE UNIQUE INDEX search_queries_unique_idx ON search_queries (query, COALESCE(city_id, -1), date_collected);
