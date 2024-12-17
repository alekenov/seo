-- Удаляем старые учетные данные GA4
DELETE FROM credentials WHERE service_name = 'ga';

-- Добавляем новые учетные данные GA4
INSERT INTO credentials (service_name, credentials, description)
VALUES (
    'ga',
    '{
        "property_id": "252026944",
        "service_account_path": "/Users/alekenov/CascadeProjects/seobot/dashbords-373217-8b5b413282cb.json"
    }'::jsonb,
    'Google Analytics 4 credentials'
);
