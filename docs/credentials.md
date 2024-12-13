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



- gsc.client_id         # ID клиента из Google Cloud Console
- gsc.client_secret     # Секрет клиента из Google Cloud Console
- gsc.auth_uri         # https://accounts.google.com/o/oauth2/auth
- gsc.token_uri        # https://oauth2.googleapis.com/token
- gsc.site_url         # URL сайта в формате sc-domain:example.com
- gsc.refresh_token    # Токен обновления (получаем через OAuth2)


src/
├── services/
│   └── gsc_service.py              # Основной класс для работы с GSC API
├── utils/
│   └── credentials_manager.py      # Класс для работы с учетными данными
└── scripts/
    ├── get_new_refresh_token.py    # Скрипт для получения нового refresh_token
    ├── update_refresh_token.py     # Скрипт для обновления refresh_token в БД
    └── check_credentials.py        # Скрипт для проверки учетных данных



    # 1. Проверяем наличие всех учетных данных:
python3 src/scripts/check_credentials.py

# 2. Если refresh_token отсутствует или устарел, получаем новый:
python3 src/scripts/get_new_refresh_token.py
# Этот скрипт:
# - Создает временный client_secrets.json из данных в БД
# - Открывает браузер для авторизации
# - Получает новый refresh_token
# - Выводит его в консоль

# 3. Обновляем refresh_token в базе:
python3 src/scripts/update_refresh_token.py
# Этот скрипт обновляет refresh_token в таблице credentials

# 4. После этого GSCService будет автоматически:
# - Получать учетные данные из базы
# - Создавать объект credentials
# - Использовать refresh_token для получения access_token
# - Автоматически обновлять access_token при необходимости