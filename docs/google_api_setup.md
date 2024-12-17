# Настройка доступа к Google APIs (Search Console и Analytics)

## Шаг 1: Создание проекта в Google Cloud Console

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Войдите в свой аккаунт Google
3. Нажмите на выпадающее меню вверху страницы и выберите "Новый проект"
4. Введите название проекта (например, "SEO Bot")
5. Нажмите "Создать"

## Шаг 2: Включение необходимых API

1. В боковом меню выберите "APIs & Services" > "Library"
2. Включите следующие API:
   - Google Search Console API
   - Google Analytics Data API (GA4)

## Шаг 3: Создание Service Account

1. В боковом меню выберите "APIs & Services" > "Credentials"
2. Нажмите "Create Credentials" > "Service Account"
3. Заполните форму:
   - Service account name: SEO Bot
   - Service account ID: будет сгенерирован автоматически
   - Description: Service Account для доступа к GSC и GA4
4. Нажмите "Create and Continue"
5. Добавьте роли (не обязательно, так как права будут выданы в самих сервисах)
6. Нажмите "Done"
7. В списке Service Accounts нажмите на созданный аккаунт
8. Перейдите на вкладку "Keys"
9. Нажмите "Add Key" > "Create new key"
10. Выберите формат JSON
11. Скачайте файл и переименуйте его в `dashbords-373217-20faafe15e3f.json`

## Шаг 4: Настройка доступа в Google Search Console

1. Перейдите в [Google Search Console](https://search.google.com/search-console)
2. Выберите нужный сайт
3. Нажмите "Настройки" (шестеренка) > "Пользователи и права"
4. Нажмите "Добавить пользователя"
5. Введите email сервисного аккаунта:
   ```
   bots-457@dashbords-373217.iam.gserviceaccount.com
   ```
6. Выберите роль "Владелец" или "Пользователь с полным доступом"
7. Нажмите "Добавить"

## Шаг 5: Настройка доступа в Google Analytics 4

1. Перейдите в [Google Analytics](https://analytics.google.com/)
2. Выберите нужный аккаунт и ресурс
3. Перейдите в "Администратор" > "Управление доступом на уровне аккаунта"
4. Нажмите "+" > "Добавить пользователей"
5. Введите email сервисного аккаунта:
   ```
   bots-457@dashbords-373217.iam.gserviceaccount.com
   ```
6. Выберите роль "Читатель" или выше
7. Нажмите "Добавить"

## Шаг 6: Установка файла сервисного аккаунта

1. Поместите скачанный `dashbords-373217-20faafe15e3f.json` в корневую папку проекта:
```bash
mv ~/Downloads/dashbords-373217-20faafe15e3f.json /Users/alekenov/CascadeProjects/seobot/
```

## Важные примечания

1. Храните файл сервисного аккаунта в безопасном месте и никогда не публикуйте его
2. Добавьте `*.json` в ваш `.gitignore` для защиты конфиденциальных данных
3. В отличие от OAuth2, сервисный аккаунт не требует интерактивной авторизации
4. Используется один сервисный аккаунт для всех Google сервисов:
   - Email: `bots-457@dashbords-373217.iam.gserviceaccount.com`
   - Project ID: `dashbords-373217`
   - Файл: `dashbords-373217-20faafe15e3f.json`

## Проверка настроек

После установки сервисного аккаунта, вы можете проверить настройки:

1. Для Google Search Console:
```bash
python3 src/scripts/test_gsc_service.py
```

2. Для Google Analytics:
```bash
python3 src/scripts/test_ga_service.py
```

Если всё настроено правильно, вы увидите данные из соответствующих сервисов.
