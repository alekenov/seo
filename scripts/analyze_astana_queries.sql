-- Анализ запросов по Астане
WITH astana_queries AS (
    SELECT 
        query,
        SUM(clicks) as total_clicks,
        SUM(impressions) as total_impressions,
        ROUND(AVG(position)::numeric, 2) as avg_position,
        ROUND((SUM(clicks)::float / NULLIF(SUM(impressions), 0) * 100)::numeric, 2) as ctr
    FROM search_console_data
    WHERE 
        (query ILIKE '%астана%' OR query ILIKE '%nur-sultan%')
        AND date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY query
    HAVING SUM(impressions) > 100
),
query_categories AS (
    SELECT
        CASE 
            WHEN query ILIKE '%доставка%' THEN 'Доставка'
            WHEN query ILIKE '%недорого%' OR query ILIKE '%дешев%' THEN 'Цена'
            WHEN query ILIKE '%круглосуточно%' THEN 'Время работы'
            WHEN query ILIKE '%заказать%' OR query ILIKE '%купить%' THEN 'Покупка'
            WHEN query ILIKE '%свадьб%' THEN 'Свадьба'
            WHEN query ILIKE '%подарок%' OR query ILIKE '%подарка%' THEN 'Подарки'
            ELSE 'Общие'
        END as category,
        query,
        total_clicks,
        total_impressions,
        avg_position,
        ctr
    FROM astana_queries
)
SELECT 
    category,
    COUNT(*) as queries_count,
    SUM(total_clicks) as category_clicks,
    SUM(total_impressions) as category_impressions,
    ROUND(AVG(avg_position)::numeric, 2) as category_avg_position,
    ROUND((SUM(total_clicks)::float / NULLIF(SUM(total_impressions), 0) * 100)::numeric, 2) as category_ctr,
    STRING_AGG(query || ' (' || total_clicks || ' clicks)', ', ' ORDER BY total_clicks DESC) as top_queries
FROM query_categories
GROUP BY category
ORDER BY category_clicks DESC;
