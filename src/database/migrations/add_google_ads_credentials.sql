-- Добавляем учетные данные для Google Ads API
INSERT INTO credentials (service_name, key_name, key_value, description) VALUES
('google_ads', 'service_account_email', 'bot-507@thinking-field-415009.iam.gserviceaccount.com', 'Google Ads service account email'),
('google_ads', 'service_account_file', 'thinking-field-415009-ddb12ae41a92.json', 'Path to service account JSON file'),
('google_ads', 'developer_token', 'iZkxUkneSPvNl8z4Wr1j2A', 'Google Ads API developer token'),
('google_ads', 'customer_id', '4986303901', 'Google Ads customer ID without dashes')
ON CONFLICT (service_name, key_name) DO UPDATE 
SET key_value = EXCLUDED.key_value,
    description = EXCLUDED.description;
