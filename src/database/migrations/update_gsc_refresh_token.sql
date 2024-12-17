-- Обновляем refresh_token для GSC
INSERT INTO credentials (service_name, key_name, key_value, description) 
VALUES ('gsc', 'refresh_token', '1//0cwYS9oY63rehCgYIARAAGAwSNwF-L9Ir1TMv8cVvRhV42Dpfr4cdgTAgtA8Gw26LCmh3EQ66MteWw7AMo-_l4HRP4w5YvuUQX_c', 'GSC refresh token')
ON CONFLICT (service_name, key_name) DO UPDATE 
SET key_value = EXCLUDED.key_value,
    description = EXCLUDED.description;
