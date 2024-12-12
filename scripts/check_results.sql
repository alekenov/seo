-- Проверяем количество запросов по типам
SELECT query_type, COUNT(*), 
       ROUND(AVG(position)::numeric, 2) as avg_position,
       ROUND(AVG(clicks)::numeric, 2) as avg_clicks,
       ROUND(AVG(impressions)::numeric, 2) as avg_impressions,
       ROUND(AVG(ctr)::numeric, 4) as avg_ctr
FROM search_queries
GROUP BY query_type
ORDER BY COUNT(*) DESC;

-- Проверяем топ-10 запросов по кликам
SELECT query, city_id, clicks, impressions, position, ctr
FROM search_queries
ORDER BY clicks DESC
LIMIT 10;

-- Проверяем распределение по городам
SELECT c.name, COUNT(*) as query_count,
       ROUND(AVG(sq.position)::numeric, 2) as avg_position,
       ROUND(AVG(sq.clicks)::numeric, 2) as avg_clicks
FROM search_queries sq
JOIN cities c ON sq.city_id = c.id
GROUP BY c.name
ORDER BY query_count DESC;
