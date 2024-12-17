-- Удаляем старые учетные данные Google Ads
DELETE FROM credentials WHERE service_name = 'google_ads';

-- Добавление учетных данных Google Ads
INSERT INTO credentials (service_name, credentials)
VALUES (
    'google_ads',
    '{
        "customer_id": "1234567890",
        "developer_token": "your_developer_token",
        "service_account_path": "dashbords-373217-20faafe15e3f.json"
    }'::jsonb
);
