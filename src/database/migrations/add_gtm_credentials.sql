-- Удаляем старые учетные данные GTM
DELETE FROM credentials WHERE service_name = 'gtm';

-- Добавление учетных данных Google Tag Manager
INSERT INTO credentials (service_name, credentials)
VALUES (
    'gtm',
    '{
        "account_id": "6261925260",
        "container_id": "202291559",
        "service_account_path": "dashbords-373217-8b5b413282cb.json"
    }'::jsonb
);
