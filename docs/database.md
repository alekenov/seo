# База данных SEO Bot

## Общая информация
- **Тип БД**: PostgreSQL (Supabase)
- **Хост**: aws-0-eu-central-1.pooler.supabase.com
- **Порт**: 6543
- **База данных**: postgres

## Структура базы данных

### Таблицы

#### 1. cities
Хранение информации о городах
- `id` (SERIAL PRIMARY KEY)
- `name` (VARCHAR(100)) - название города
- `name_en` (VARCHAR(100)) - английское название
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

#### 2. search_queries
Поисковые запросы с категоризацией
- `id` (SERIAL PRIMARY KEY)
- `query` (TEXT) - текст запроса
- `query_type` (ENUM) - тип запроса (delivery, flowers, bouquets, gifts, other)
- `city_id` (INTEGER) - связь с городом
- `created_at` (TIMESTAMPTZ)

#### 3. daily_metrics
Ежедневные метрики по запросам
- `id` (SERIAL PRIMARY KEY)
- `date` (DATE)
- `query_id` (INTEGER)
- `clicks` (INTEGER)
- `impressions` (INTEGER)
- `position` (FLOAT)
- `ctr` (FLOAT)
- `url` (TEXT)
- `created_at` (TIMESTAMPTZ)

#### 4. weekly_metrics
Агрегированные недельные метрики
- `id` (SERIAL PRIMARY KEY)
- `week_start` (DATE)
- `query_id` (INTEGER)
- `avg_clicks` (FLOAT)
- `total_clicks` (INTEGER)
- `avg_impressions` (FLOAT)
- `total_impressions` (INTEGER)
- `avg_position` (FLOAT)
- `avg_ctr` (FLOAT)
- `created_at` (TIMESTAMPTZ)

#### 5. monthly_metrics
Агрегированные месячные метрики
- Структура аналогична weekly_metrics

#### 6. position_changes
Отслеживание изменений позиций
- `id` (SERIAL PRIMARY KEY)
- `query_id` (INTEGER)
- `date` (DATE)
- `old_position` (FLOAT)
- `new_position` (FLOAT)
- `change_percent` (FLOAT)
- `created_at` (TIMESTAMPTZ)

#### 7. anomalies
Фиксация аномальных изменений
- `id` (SERIAL PRIMARY KEY)
- `query_id` (INTEGER)
- `date` (DATE)
- `metric_type` (VARCHAR(50))
- `expected_value` (FLOAT)
- `actual_value` (FLOAT)
- `deviation_percent` (FLOAT)
- `created_at` (TIMESTAMPTZ)

## Индексы
- idx_search_queries_city на search_queries(city_id)
- idx_daily_metrics_date на daily_metrics(date)
- idx_daily_metrics_query на daily_metrics(query_id)
- idx_weekly_metrics_date на weekly_metrics(week_start)
- idx_monthly_metrics_date на monthly_metrics(month_start)
- idx_position_changes_date на position_changes(date)
- idx_anomalies_date на anomalies(date)

## Триггеры
- update_cities_updated_at: Автоматическое обновление updated_at при изменении записи в таблице cities

## Ограничения и связи
- Внешние ключи между таблицами для обеспечения целостности данных
- Уникальные ограничения на комбинации полей для предотвращения дубликатов
- Проверки на корректность значений метрик

## Оптимизация
- Использование пула соединений для эффективного управления подключениями
- Индексы на часто используемых полях для ускорения запросов
- Партиционирование по дате для больших таблиц (планируется)
