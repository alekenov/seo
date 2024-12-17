# Рабочий процесс SEO Bot

## Подключение к базе данных Supabase

### Конфигурация и учетные данные

1. **Файл конфигурации** `/src/config/supabase_config.py`
   ```python
   SUPABASE_URL = "https://jvfjxlpplbyrafasobzl.supabase.co"
   SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2Zmp4bHBwbGJ5cmFmYXNvYnpsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM4OTg2NzUsImV4cCI6MjA0OTQ3NDY3NX0.1_tTwBDg1ibnlBbe6PyzID8CucrkQlXEUsA5dyNQ_g0"
   SUPABASE_SERVICE_ROLE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2Zmp4bHBwbGJ5cmFmYXNvYnpsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzg5ODY3NSwiZXhwIjoyMDQ5NDc0Njc1fQ.sk2X5le3Rt3O0krvJREk0Cn4H8bI3V2rwx5Md2jg_SI"
   
   # Database connection string
   DATABASE_URL = "postgresql://postgres.jvfjxlpplbyrafasobzl:fogdif-7voHxi-ryfqug@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
   ```

2. **Способы подключения**
   - **Через Supabase API** (`/src/database/supabase_client.py`):
     ```python
     from supabase import create_client
     
     class SupabaseClient:
         def __init__(self):
             self.client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
     ```
   
   - **Прямое подключение к PostgreSQL** (`/src/utils/credentials_manager.py`):
     ```python
     import psycopg2
     
     class CredentialsManager:
         def __init__(self):
             self.db_url = DATABASE_URL
             
         def _get_connection(self):
             return psycopg2.connect(self.db_url)
     ```

3. **Использование**
   - `SupabaseClient` - для работы с таблицами через API
   - `CredentialsManager` - для прямого доступа к базе данных

## Настройка учетных данных

### Google Search Console

1. **Service Account**
   - Создайте проект в Google Cloud Console
   - Включите Google Search Console API
   - Создайте Service Account и скачайте JSON файл с ключами
   - Добавьте Service Account как пользователя в Google Search Console
   - Поместите JSON файл в корневую директорию проекта

2. **Таблица credentials**
   ```sql
   INSERT INTO credentials (service_name, credential_name, credential_value)
   VALUES 
   ('gsc', 'site_url', 'sc-domain:cvety.kz'),
   ('gsc', 'service_account_path', '/path/to/service-account.json');
   ```

### Google Analytics

1. **Service Account**
   - В том же проекте Google Cloud Console
   - Включите Google Analytics Data API
   - Используйте тот же Service Account
   - Добавьте Service Account как пользователя в Google Analytics
   - Используйте тот же JSON файл с ключами

2. **Таблица credentials**
   ```sql
   INSERT INTO credentials (service_name, credential_name, credential_value)
   VALUES 
   ('ga', 'property_id', 'your-property-id'),
   ('ga', 'service_account_path', '/path/to/service-account.json');
   ```

### Google Tag Manager

1. **Service Account**
   - В том же проекте Google Cloud Console
   - Включите Google Tag Manager API
   - Используйте тот же Service Account
   - Добавьте Service Account как пользователя в GTM с правами на чтение
   - Используйте тот же JSON файл с ключами

2. **Таблица credentials**
   ```sql
   INSERT INTO credentials (service_name, credential_name, credential_value)
   VALUES 
   ('gtm', 'account_id', 'your-account-id'),
   ('gtm', 'container_id', 'your-container-id'),
   ('gtm', 'service_account_path', '/path/to/service-account.json');
   ```

3. **Использование GTMService**
   ```python
   from services.gtm_service import GTMService
   
   # Инициализация
   gtm = GTMService()
   
   # Получение информации о тегах
   tags = gtm.get_tags()
   
   # Анализ контейнера
   analysis = gtm.analyze_container()
   print(f"Всего тегов: {analysis['summary']['total_tags']}")
   print(f"GA4 теги: {analysis['tags']['ga4_tags']}")
   ```

### Telegram

1. **Бот и канал**
   ```sql
   INSERT INTO credentials (service_name, credential_name, credential_value)
   VALUES 
   ('telegram', 'bot_token', 'your-bot-token'),
   ('telegram', 'channel_id', 'your-channel-id');
   ```

## Управление учетными данными

### CredentialsManager

Класс `CredentialsManager` используется для централизованного управления всеми учетными данными:

```python
from utils.credentials_manager import CredentialsManager

# Инициализация
credentials_manager = CredentialsManager()

# Получение учетных данных
site_url = credentials_manager.get_credential('gsc', 'site_url')
property_id = credentials_manager.get_credential('ga', 'property_id')
bot_token = credentials_manager.get_credential('telegram', 'bot_token')
```

### Безопасность

- Все учетные данные хранятся в таблице `credentials` в Supabase
- Service Account JSON файл хранится локально и не должен попадать в Git
- Добавьте путь к JSON файлу в `.gitignore`

## Авторизация в Google Search Console

### Процесс получения и сохранения учетных данных

1. **Первый запуск и авторизация**
   - При первом запуске скрипта, если нет refresh_token в базе данных:
   - Скрипт запускает браузер и открывает страницу авторизации Google
   - После авторизации Google возвращает код
   - Скрипт обменивает код на refresh_token
   - refresh_token сохраняется в базу данных

2. **Последующие запуски**
   - Скрипт проверяет наличие refresh_token в базе
   - Если токен есть, использует его для получения access_token
   - Если токен истек или недействителен, запускает процесс авторизации заново

### Файлы и их назначение

1. `/src/services/gsc_service.py`
   ```python
   class GSCService:
       def __init__(self):
           self.credentials = CredentialsManager()
           self._init_service()
           
       def _init_service(self):
           # Проверяем наличие refresh_token
           refresh_token = self.credentials.get_credential('gsc', 'refresh_token')
           
           if not refresh_token:
               # Если токена нет, запускаем процесс авторизации
               self._start_oauth_flow()
           else:
               # Если токен есть, используем его
               self._init_with_refresh_token(refresh_token)
               
       def _start_oauth_flow(self):
           # Создаем URL для авторизации
           flow = InstalledAppFlow.from_client_secrets_file(
               'credentials.json',
               scopes=['https://www.googleapis.com/auth/webmasters.readonly']
           )
           
           # Запускаем браузер для авторизации
           credentials = flow.run_local_server(port=0)
           
           # Сохраняем полученный refresh_token
           self.credentials.set_credential(
               'gsc', 
               'refresh_token', 
               credentials.refresh_token
           )
   ```

2. `/src/utils/credentials_manager.py`
   - Управляет учетными данными в базе Supabase
   - При первом запуске таблица credentials пустая
   - Токены и креденшиалы добавляются по мере авторизации

### Процесс авторизации на примере

1. **Начальное состояние базы**
   ```sql
   -- Таблица credentials пустая или содержит только базовые настройки
   SELECT * FROM credentials WHERE service_name = 'gsc';
   -- Нет записей или только базовые настройки
   ```

2. **После первой авторизации**
   ```sql
   -- В таблицу добавляется refresh_token
   INSERT INTO credentials (service_name, key_name, key_value)
   VALUES ('gsc', 'refresh_token', 'полученный_refresh_token');
   ```

3. **Последующие запуски**
   ```python
   # Скрипт получает refresh_token из базы
   refresh_token = credentials.get_credential('gsc', 'refresh_token')
   
   # Использует его для получения access_token
   credentials = Credentials(
       token=None,  # access token будет получен автоматически
       refresh_token=refresh_token,
       client_id=client_id,
       client_secret=client_secret,
       token_uri=token_uri
   )
   ```

### Важные моменты

1. **Безопасность**
   - refresh_token сохраняется только в базе данных
   - Нет локальных файлов с токенами
   - credentials.json не содержит токенов, только параметры приложения

2. **Автоматическое обновление**
   - refresh_token живет долго (пока не отозван)
   - access_token обновляется автоматически
   - При ошибках авторизации процесс запускается заново

3. **Отладка**
   ```python
   # Проверка наличия токена
   print(credentials.get_credential('gsc', 'refresh_token'))
   
   # Если токена нет - None
   # Если есть - строка вида "1//0cJjBxFEWDuLjCgYIARAAGAwSNwF-..."
   ```

### Хранение учетных данных

1. **База данных Supabase**
   - Таблица `credentials` хранит все учетные данные
   - Структура записи:
     * `service_name` (например, 'gsc')
     * `key_name` (например, 'client_id')
     * `key_value` (значение)
     * `description` (описание)

2. **Безопасность**
   - Все чувствительные данные хранятся только в базе данных
   - Не используются .env файлы
   - Токены автоматически обновляются
   - Учетные данные никогда не логируются

### Процесс получения данных

1. **Подготовка запроса**
   ```python
   start_date = date(2024, 1, 1)
   end_date = date(2024, 1, 31)
   dimensions = ['query', 'page']
   ```

2. **Выполнение запроса**
   ```python
   data = gsc.get_search_analytics(
       start_date=start_date,
       end_date=end_date,
       dimensions=dimensions
   )
   ```

3. **Сохранение данных**
   - Результаты сохраняются в таблицу `search_queries_daily`
   - Агрегированные данные в `weekly_metrics` и `monthly_metrics`

## Настройка проекта

### Первоначальная настройка

1. Создать проект в Google Cloud Console
2. Включить Google Search Console API
3. Создать OAuth2 креденшиалы
4. Загрузить credentials.json
5. Добавить учетные данные в Supabase:
   ```sql
   INSERT INTO credentials (service_name, key_name, key_value, description)
   VALUES 
   ('gsc', 'credentials_file', 'credentials.json', 'Path to credentials file'),
   ('gsc', 'site_url', 'https://cvety.kz', 'Site URL in GSC');
   ```

### Обновление учетных данных

Для обновления учетных данных используйте CredentialsManager:
```python
from src.utils.credentials_manager import CredentialsManager

cm = CredentialsManager()
cm.set_credential('gsc', 'refresh_token', 'new_token_value')
