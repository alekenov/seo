-- Обновляем существующие записи, используя данные из GSC
UPDATE search_queries_daily
SET page_url = 'https://cvety.kz'  -- Временно устанавливаем основной URL
WHERE page_url IS NULL;
