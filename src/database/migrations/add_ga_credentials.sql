-- Удаляем старые учетные данные GA
DELETE FROM credentials WHERE service_name = 'ga';

-- Добавление учетных данных Google Analytics
INSERT INTO credentials (service_name, credentials)
VALUES (
    'ga',
    '{
        "view_id": "ga:286654169",
        "service_account_path": "dashbords-373217-20faafe15e3f.json"
    }'::jsonb
);
