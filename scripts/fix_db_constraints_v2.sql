-- Drop old constraint
ALTER TABLE search_queries DROP CONSTRAINT IF EXISTS search_queries_query_city_id_key;

-- Add new constraint with expression
CREATE UNIQUE INDEX search_queries_query_city_id_key 
    ON search_queries (query, COALESCE(city_id, -1));
