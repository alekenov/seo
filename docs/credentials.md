# Правила работы с учетными данными

## 1. Хранение учетных данных
- Все учетные данные хранятся в таблице `credentials` в Supabase
- **НЕ ИСПОЛЬЗУЙТЕ** локальные `.env` файлы для хранения учетных данных
- Файл `.env` можно удалить, так как все данные теперь в Supabase

## 2. Структура таблицы credentials
- `service_name`: название сервиса (например, 'gsc', 'telegram', 'supabase')
- `key_name`: название ключа
- `key_value`: значение
- `description`: описание

## 3. Доступные сервисы
### Google Search Console (gsc)
- client_id
- client_secret
- project_id
- auth_uri
- token_uri
- site_url
- credentials_file

### Telegram (telegram)
- bot_token
- channel_id

### Supabase (supabase)
- url
- anon_key
- service_role

## 4. Работа с учетными данными
- Используйте класс `CredentialsManager` для работы с учетными данными
- Методы:
  - `get_credential(service, key)` - получение значения
  - `set_credential(service, key, value)` - установка значения
  - `get_service_credentials(service)` - получение всех данных сервиса
  - `load_credentials(service)` - загрузка всех данных сервиса

## 5. Безопасность
- Не храните учетные данные в коде
- Не коммитьте файлы с учетными данными в Git
- Используйте только Supabase для хранения конфиденциальной информации
