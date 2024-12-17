-- Удаляем таблицу если она существует
DROP TABLE IF EXISTS credentials;

-- Создаем таблицу credentials
CREATE TABLE credentials (
    id SERIAL PRIMARY KEY,
    service_name TEXT NOT NULL,
    credentials JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
