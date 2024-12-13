-- Удаляем старые функции
DROP FUNCTION IF EXISTS get_position_changes(date, date, double precision, varchar, text);
DROP FUNCTION IF EXISTS get_position_stats(date, integer[]);

-- Функция для анализа изменений позиций
CREATE OR REPLACE FUNCTION get_position_changes(
    p_start_date date,
    p_end_date date,
    p_min_change float DEFAULT 3.0,
    p_query_type varchar DEFAULT NULL,
    p_url_pattern text DEFAULT NULL
) RETURNS TABLE (
    query text,
    url text,
    city_name varchar(255),
    old_position float,
    new_position float,
    position_change float,
    position_change_abs float,
    avg_position float,
    query_type varchar(50),
    impressions_change integer,
    clicks_change integer
) AS $$
BEGIN
    RETURN QUERY
    WITH position_data AS (
        SELECT 
            sq.query,
            sq.query_type,
            dm.url,
            c.name as city_name,
            FIRST_VALUE(dm.position) OVER (
                PARTITION BY sq.query, dm.url 
                ORDER BY dm.date
            ) as old_position,
            FIRST_VALUE(dm.position) OVER (
                PARTITION BY sq.query, dm.url 
                ORDER BY dm.date DESC
            ) as new_position,
            AVG(dm.position) OVER (
                PARTITION BY sq.query, dm.url
            ) as avg_position,
            FIRST_VALUE(dm.impressions) OVER (
                PARTITION BY sq.query, dm.url 
                ORDER BY dm.date
            ) as old_impressions,
            FIRST_VALUE(dm.impressions) OVER (
                PARTITION BY sq.query, dm.url 
                ORDER BY dm.date DESC
            ) as new_impressions,
            FIRST_VALUE(dm.clicks) OVER (
                PARTITION BY sq.query, dm.url 
                ORDER BY dm.date
            ) as old_clicks,
            FIRST_VALUE(dm.clicks) OVER (
                PARTITION BY sq.query, dm.url 
                ORDER BY dm.date DESC
            ) as new_clicks
        FROM search_queries sq
        JOIN daily_metrics dm ON sq.id = dm.query_id
        LEFT JOIN cities c ON sq.city_id = c.id
        WHERE dm.date BETWEEN p_start_date AND p_end_date
        AND (p_query_type IS NULL OR sq.query_type = p_query_type)
        AND (p_url_pattern IS NULL OR dm.url LIKE p_url_pattern)
    )
    SELECT DISTINCT
        pd.query,
        pd.url,
        pd.city_name,
        pd.old_position,
        pd.new_position,
        (pd.new_position - pd.old_position) as position_change,
        ABS(pd.new_position - pd.old_position) as position_change_abs,
        pd.avg_position,
        pd.query_type,
        (pd.new_impressions - pd.old_impressions) as impressions_change,
        (pd.new_clicks - pd.old_clicks) as clicks_change
    FROM position_data pd
    WHERE ABS(pd.new_position - pd.old_position) >= p_min_change
    ORDER BY position_change_abs DESC;
END;
$$ LANGUAGE plpgsql;

-- Функция для получения статистики по периодам
CREATE OR REPLACE FUNCTION get_position_stats(
    p_current_date date,
    p_periods integer[]
) RETURNS TABLE (
    period_days integer,
    avg_position float,
    improved_count bigint,
    declined_count bigint,
    total_queries bigint,
    significant_changes bigint
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE periods(days) AS (
        SELECT unnest(p_periods)
    ),
    period_data AS (
        SELECT 
            p.days as period_days,
            sq.query,
            dm.url,
            FIRST_VALUE(dm.position) OVER (
                PARTITION BY sq.query, dm.url, p.days
                ORDER BY dm.date
            ) as old_position,
            FIRST_VALUE(dm.position) OVER (
                PARTITION BY sq.query, dm.url, p.days
                ORDER BY dm.date DESC
            ) as new_position,
            AVG(dm.position) OVER (
                PARTITION BY sq.query, dm.url, p.days
            ) as avg_position
        FROM periods p
        CROSS JOIN search_queries sq
        JOIN daily_metrics dm ON sq.id = dm.query_id
        WHERE dm.date BETWEEN (p_current_date - p.days) AND p_current_date
    )
    SELECT 
        pd.period_days,
        AVG(pd.avg_position) as avg_position,
        COUNT(*) FILTER (WHERE pd.new_position < pd.old_position) as improved_count,
        COUNT(*) FILTER (WHERE pd.new_position > pd.old_position) as declined_count,
        COUNT(DISTINCT pd.query) as total_queries,
        COUNT(*) FILTER (WHERE ABS(pd.new_position - pd.old_position) >= 3.0) as significant_changes
    FROM period_data pd
    GROUP BY pd.period_days
    ORDER BY pd.period_days;
END;
$$ LANGUAGE plpgsql;

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_daily_metrics_position ON daily_metrics(position);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date_position ON daily_metrics(date, position);
CREATE INDEX IF NOT EXISTS idx_search_queries_query_type_date ON search_queries(query_type, date_collected);
