-- Удаляем старую таблицу
DROP TABLE IF EXISTS credentials CASCADE;

-- Создаем таблицу для хранения учетных данных
CREATE TABLE IF NOT EXISTS credentials (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(50) NOT NULL,
    key_name VARCHAR(50) NOT NULL,
    key_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_name, key_name)
);

-- Создаем функцию для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Удаляем старый триггер
DROP TRIGGER IF EXISTS update_credentials_updated_at ON credentials;

-- Создаем триггер для автоматического обновления updated_at
CREATE TRIGGER update_credentials_updated_at
    BEFORE UPDATE ON credentials
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Вставляем начальные данные
INSERT INTO credentials (service_name, key_name, key_value, description) VALUES
('supabase', 'url', '${SUPABASE_URL}', 'Supabase project URL'),
('supabase', 'anon_key', '${SUPABASE_ANON_KEY}', 'Supabase anonymous key'),
('supabase', 'service_role', '${SUPABASE_SERVICE_ROLE}', 'Supabase service role key'),
('gsc', 'site_url', '${GSC_SITE_URL}', 'Google Search Console site URL'),
('gsc', 'credentials_file', 'credentials.json', 'Path to GSC credentials file'),
('gsc', 'project_id', '${GSC_PROJECT_ID}', 'Google Cloud Project ID'),
('gsc', 'client_id', '${GSC_CLIENT_ID}', 'Google OAuth client ID'),
('gsc', 'client_secret', '${GSC_CLIENT_SECRET}', 'Google OAuth client secret'),
('gsc', 'auth_uri', 'https://accounts.google.com/o/oauth2/auth', 'Google OAuth auth URI'),
('gsc', 'token_uri', 'https://oauth2.googleapis.com/token', 'Google OAuth token URI'),
('telegram', 'bot_token', '${TELEGRAM_BOT_TOKEN}', 'Telegram bot token'),
('telegram', 'channel_id', '${TELEGRAM_CHANNEL_ID}', 'Telegram channel ID')
ON CONFLICT (service_name, key_name) DO UPDATE 
SET key_value = EXCLUDED.key_value,
    description = EXCLUDED.description;
