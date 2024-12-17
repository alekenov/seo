-- Удаляем старый refresh_token
DELETE FROM credentials 
WHERE service_name = 'gsc' AND key_name = 'refresh_token';
