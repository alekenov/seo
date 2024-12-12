-- Анализ запросов с доставкой по городам
WITH delivery_queries AS (
    SELECT 
        sq.query,
        c.name as city,
        sq.position,
        sq.clicks,
        sq.impressions,
        sq.ctr,
        CASE 
            WHEN position <= 3 THEN 'top3'
            WHEN position <= 5 THEN 'top5'
            ELSE 'other'
        END as position_group
    FROM search_queries sq
    LEFT JOIN cities c ON sq.city_id = c.id
    WHERE 
        (query LIKE '%доставка%цветов%' OR 
         query LIKE '%цветы%доставка%' OR
         query LIKE '%заказать%цветы%' OR
         query LIKE 'цветы%' OR
         query LIKE '%flower delivery%')
        AND query NOT LIKE '%cvety%'
        AND query NOT LIKE '%кз%'
        AND query NOT LIKE '%kz%'
)
SELECT 
    city,
    COUNT(*) as total_queries,
    ROUND(AVG(position)::numeric, 2) as avg_position,
    ROUND(AVG(clicks)::numeric, 2) as avg_clicks,
    ROUND(AVG(ctr)::numeric, 4) as avg_ctr,
    SUM(CASE WHEN position_group = 'top3' THEN 1 ELSE 0 END) as in_top3,
    SUM(CASE WHEN position_group = 'top5' THEN 1 ELSE 0 END) as in_top5,
    STRING_AGG(CASE WHEN clicks > 50 THEN query ELSE NULL END, ', ') as top_queries
FROM delivery_queries
WHERE city IS NOT NULL
GROUP BY city
ORDER BY total_queries DESC;
