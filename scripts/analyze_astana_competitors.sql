-- Анализ конкурентов по Астане
WITH competitor_pages AS (
    SELECT 
        page,
        SUM(clicks) as total_clicks,
        SUM(impressions) as total_impressions,
        ROUND(AVG(position)::numeric, 2) as avg_position,
        ROUND((SUM(clicks)::float / NULLIF(SUM(impressions), 0) * 100)::numeric, 2) as ctr
    FROM search_console_data
    WHERE 
        (query ILIKE '%астана%' OR query ILIKE '%nur-sultan%')
        AND date >= CURRENT_DATE - INTERVAL '30 days'
        AND page NOT LIKE '%cvety.kz%'
    GROUP BY page
    HAVING SUM(impressions) > 100
),
domain_stats AS (
    SELECT
        REGEXP_REPLACE(page, '^https?://([^/]+)/.*$', '\1') as domain,
        COUNT(DISTINCT page) as pages_count,
        SUM(total_clicks) as domain_clicks,
        SUM(total_impressions) as domain_impressions,
        ROUND(AVG(avg_position)::numeric, 2) as domain_avg_position,
        ROUND((SUM(total_clicks)::float / NULLIF(SUM(total_impressions), 0) * 100)::numeric, 2) as domain_ctr
    FROM competitor_pages
    GROUP BY domain
)
SELECT 
    domain,
    pages_count,
    domain_clicks,
    domain_impressions,
    domain_avg_position,
    domain_ctr,
    ROUND((domain_clicks::float / NULLIF((SELECT SUM(domain_clicks) FROM domain_stats), 0) * 100)::numeric, 2) as market_share
FROM domain_stats
ORDER BY domain_clicks DESC
LIMIT 10;
