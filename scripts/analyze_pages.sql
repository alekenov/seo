-- Анализ страниц по городам
WITH city_pages AS (
    SELECT 
        dm.url,
        dm.clicks,
        dm.impressions,
        dm.position,
        dm.ctr,
        CASE 
            WHEN url LIKE '%/almaty/%' THEN 'Алматы'
            WHEN url LIKE '%/astana/%' OR url LIKE '%/nur-sultan/%' THEN 'Астана'
        END as city
    FROM daily_metrics dm
    WHERE url LIKE '%/almaty/%' 
       OR url LIKE '%/astana/%' 
       OR url LIKE '%/nur-sultan/%'
)
SELECT 
    city,
    url,
    clicks,
    impressions,
    ROUND(position::numeric, 2) as position,
    ROUND(ctr::numeric, 4) as ctr
FROM city_pages
WHERE clicks > 0
ORDER BY clicks DESC
LIMIT 20;
