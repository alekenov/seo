# Структура кодовой базы SEO Bot

## 1. Структура проекта

### Основные директории
```
seobot/
├── src/                    # Исходный код
│   ├── analytics/         # Модули аналитики
│   ├── database/         # Работа с базой данных
│   └── config/           # Конфигурационные файлы
├── scripts/               # Скрипты для анализа и обработки
├── docs/                  # Документация
├── tests/                # Тесты
└── dataset/              # Наборы данных
```

### Ключевые файлы
- `src/config/supabase_config.py` - конфигурация Supabase
- `.env` - переменные окружения
- `requirements.txt` - зависимости проекта
- `run_analysis.py` - основной скрипт анализа

## 2. Конфигурация и доступы

### Supabase
- **Конфиг**: `src/config/supabase_config.py`
- **Переменные**:
  - SUPABASE_URL
  - SUPABASE_ANON_KEY
  - SUPABASE_SERVICE_ROLE
  - DB_PASSWORD
  - DATABASE_URL

### Google Search Console
- **Креды**: `config/credentials.json`
- **Переменные окружения**:
  - GSC_CLIENT_ID
  - GSC_CLIENT_SECRET

### Google Analytics
- **Креды**: `dashbords-373217-ba2bbe59eb47.json`
- **Тип авторизации**: Service Account
- **Доступ**: 
  - Создан сервисный аккаунт в Google Cloud Console
  - Выданы права на просмотр данных GA4
  - Используется библиотека google-analytics-data-v1beta
- **Параметры**:
  - PROPERTY_ID: "373217"
  - Credentials хранятся в таблице credentials в Supabase

### Яндекс.Метрика
- **Авторизация**: OAuth токен
- **Токен**: Хранится в таблице credentials в Supabase
- **Параметры**:
  - COUNTER_ID: "87226571"
  - Используется библиотека tapi-yandex-metrika
- **Доступ**:
  - Создано приложение в Яндекс OAuth
  - Выданы права на чтение данных метрики
  - Токен получен через OAuth авторизацию

### CRM API
- **Авторизация**: API токен
- **Токен**: "ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144"
- **Endpoint**: "https://cvety.kz/api/order/order-list"
- **Параметры запроса**:
  - access_token
  - limit
  - status_id

## 3. База данных

### Основные таблицы
1. **search_queries**
   - Поисковые запросы
   - Связь с городами
   - Основные метрики

2. **daily_metrics**
   - Ежедневная статистика
   - Клики, показы, CTR, позиции

3. **cities**
   - Список городов
   - Связь с запросами

4. **position_changes**
   - История изменения позиций
   - Анализ динамики

### Часто используемые запросы
- Топ-10 запросов: `scripts/analyze_top_queries.py`
- Анализ позиций: `src/analytics/position_analysis.py`
- Анализ CTR: `src/analytics/ctr_analysis.py`

## 4. Аналитические модули

### Position Analyzer
- **Файл**: `src/analytics/position_analysis.py`
- **Функции**:
  - Анализ изменения позиций
  - Выявление трендов
  - Группировка по категориям

### CTR Analyzer
- **Файл**: `src/analytics/ctr_analysis.py`
- **Функции**:
  - Анализ CTR по позициям
  - Выявление аномалий
  - Рекомендации по улучшению

### Live Analyzer
- **Файл**: `src/analytics/live_analysis.py`
- **Функции**:
  - Работа с GSC API
  - Сохранение в Supabase
  - Анализ в реальном времени

## 5. Часто используемые скрипты

### Анализ данных
- `scripts/analyze_top_queries.py` - анализ топ запросов
- `scripts/test_analytics.py` - тестирование аналитики
- `examples/analyze_category.py` - анализ по категориям

### Работа с данными
- `scripts/add_queries.py` - добавление запросов
- `scripts/test_data.py` - генерация тестовых данных

## 6. Рабочий процесс

### Добавление новых функций
1. Создать ветку от main
2. Добавить код в соответствующую директорию
3. Обновить документацию
4. Создать PR

### Обновление документации
- Обновлять changelog.md
- Отмечать выполненные задачи в todo.md
- Добавлять примеры использования

## 7. Отладка и тестирование

### Запуск тестов
```bash
python -m pytest tests/
```

### Типичные проблемы
1. Ошибки авторизации в Supabase
   - Проверить креды в supabase_config.py
   - Проверить права доступа

2. Проблемы с GSC API
   - Обновить токены
   - Проверить credentials.json

## 8. Полезные ссылки

### API Документация
- [Google Search Console API](https://developers.google.com/webmaster-tools/search-console-api-original)
- [Supabase Docs](https://supabase.com/docs)

### Внутренние документы
- [TODO List](docs/todo.md)
- [Changelog](changelog.md)
- [Development Plan](docs/plans.md)
