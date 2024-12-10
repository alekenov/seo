# Настройка доступа к Google Search Console API

## Шаг 1: Создание проекта в Google Cloud Console

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Войдите в свой аккаунт Google
3. Нажмите на выпадающее меню вверху страницы и выберите "Новый проект"
4. Введите название проекта (например, "SEO Data Collector")
5. Нажмите "Создать"

## Шаг 2: Включение Google Search Console API

1. В боковом меню выберите "APIs & Services" > "Library"
2. В поиске введите "Search Console API"
3. Выберите "Google Search Console API"
4. Нажмите кнопку "Enable" (Включить)

## Шаг 3: Создание учетных данных (credentials)

1. В боковом меню выберите "APIs & Services" > "Credentials"
2. Нажмите "Create Credentials" > "OAuth client ID"
3. Если это первый раз:
   - Нажмите "Configure Consent Screen"
   - Выберите "External" (если нет G Suite) или "Internal"
   - Заполните обязательные поля (имя приложения, email поддержки)
   - В разделе "Scopes" добавьте "https://www.googleapis.com/auth/webmasters.readonly"
   - Сохраните настройки

4. Вернитесь к созданию OAuth client ID:
   - Application type: Desktop application
   - Name: SEO Data Collector (или любое другое)
   - Нажмите "Create"

5. Скачайте JSON файл с учетными данными:
   - После создания появится окно с данными
   - Нажмите "Download JSON"
   - Переименуйте скачанный файл в `credentials.json`

## Шаг 4: Установка credentials.json

1. Поместите скачанный `credentials.json` в папку `config/` вашего проекта:
```bash
mv ~/Downloads/credentials.json /Users/alekenov/CascadeProjects/seobot/config/
```

## Шаг 5: Добавление сайта в Google Search Console

1. Перейдите в [Google Search Console](https://search.google.com/search-console)
2. Добавьте и верифицируйте ваш сайт, если еще не сделали это
3. Запишите URL вашего сайта - он понадобится при использовании API

## Важные примечания

1. Храните `credentials.json` в безопасном месте и никогда не публикуйте его
2. Добавьте `config/credentials.json` в ваш `.gitignore`
3. При первом запуске программы потребуется авторизация через браузер
4. Токен доступа будет автоматически сохранен и использован для последующих запросов

## Проверка настроек

После установки credentials.json, вы можете проверить настройки, запустив тестовый скрипт:

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Проверка авторизации
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

flow = InstalledAppFlow.from_client_secrets_file(
    'config/credentials.json', SCOPES)
credentials = flow.run_local_server(port=0)

# Создание сервиса
service = build('searchconsole', 'v1', credentials=credentials)

# Получение списка сайтов
sites = service.sites().list().execute()
print(sites)
```

Если всё настроено правильно, вы увидите список ваших сайтов из Search Console.
