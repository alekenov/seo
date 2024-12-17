-- Добавление учетных данных Google Analytics
INSERT INTO credentials (service_name, credential_name, credential_value)
VALUES 
('ga', 'property_id', '411584206'),  -- Замените на ваш property_id
('ga', 'service_account_path', 'dashbords-373217-20faafe15e3f.json');  -- Путь к файлу service account
