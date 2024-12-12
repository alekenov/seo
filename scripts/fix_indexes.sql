-- Удаляем все конфликтующие индексы и ограничения
DROP INDEX IF EXISTS search_queries_query_city_date_idx;
DROP INDEX IF EXISTS search_queries_query_city_id_key;
ALTER TABLE search_queries DROP CONSTRAINT IF EXISTS search_queries_query_date_collected_key;
DROP INDEX IF EXISTS search_queries_unique_idx;

-- Создаем один правильный индекс
CREATE UNIQUE INDEX search_queries_unique_idx ON search_queries (query, COALESCE(city_id, -1), date_collected);
