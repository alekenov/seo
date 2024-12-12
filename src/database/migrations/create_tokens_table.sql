-- Создаем таблицу для хранения токенов
CREATE TABLE IF NOT EXISTS tokens (
    id SERIAL PRIMARY KEY,
    service VARCHAR(50) NOT NULL,
    token_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service)
);
