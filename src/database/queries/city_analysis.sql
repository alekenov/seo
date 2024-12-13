-- Анализ запросов по городам
WITH query_stats AS (
    SELECT 
        query_type,
        SUBSTRING(query_type FROM '.*_(.*)$') as city,
        COUNT(*) as query_count,
        SUM(clicks) as total_clicks,
        SUM(impressions) as total_impressions,
        AVG(position) as avg_position,
        AVG(CASE WHEN impressions > 0 THEN clicks::float / impressions ELSE 0 END) as avg_ctr
    FROM search_queries
    WHERE query_type LIKE '%\_%' -- Только запросы с городами
    AND date_collected >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY query_type, SUBSTRING(query_type FROM '.*_(.*)$')
)
SELECT 
    city,
    COUNT(DISTINCT query_type) as category_count,
    SUM(query_count) as total_queries,
    SUM(total_clicks) as city_clicks,
    SUM(total_impressions) as city_impressions,
    AVG(avg_position) as city_avg_position,
    AVG(avg_ctr) as city_avg_ctr,
    ARRAY_AGG(query_type ORDER BY total_clicks DESC) as top_categories
FROM query_stats
GROUP BY city
ORDER BY city_clicks DESC;
