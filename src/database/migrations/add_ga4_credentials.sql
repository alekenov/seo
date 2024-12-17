-- Удаляем старые учетные данные GA4
DELETE FROM credentials WHERE service_name = 'ga4';

-- Добавление учетных данных Google Analytics 4
INSERT INTO credentials (service_name, credentials)
VALUES (
    'ga4',
    '{
        "measurement_id": "G-X0F3KBN3ZT",
        "service_account_path": "dashbords-373217-20faafe15e3f.json"
    }'::jsonb
);
