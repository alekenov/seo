# План разработки Marketing Bots

## Этап 1: Подготовка инфраструктуры (2 недели)

### 1.1 Настройка базовой структуры проекта
- [ ] Создание структуры директорий
- [ ] Настройка виртуального окружения
- [ ] Создание базового README.md
- [ ] Настройка .gitignore

### 1.2 Настройка базы данных
- [ ] Создание общих таблиц для всех платформ
- [ ] Создание специфичных таблиц для Google Ads
- [ ] Создание специфичных таблиц для Instagram Ads
- [ ] Настройка индексов и оптимизация

### 1.3 Настройка системы конфигурации
- [ ] Создание шаблонов конфигурационных файлов
- [ ] Настройка системы управления секретами
- [ ] Создание примеров конфигурации

## Этап 2: Разработка ядра системы (3 недели)

### 2.1 Базовые классы и интерфейсы
```python
# Пример структуры abstract_bot.py
class AdvertisingBot:
    def collect_data(self)
    def analyze_performance(self)
    def optimize_campaign()
    def generate_report()
```

### 2.2 Общие компоненты
- [ ] Разработка data_processor.py
- [ ] Разработка db_handler.py
- [ ] Создание системы метрик
- [ ] Разработка системы логирования

### 2.3 Система отчетности
- [ ] Создание базовых шаблонов отчетов
- [ ] Разработка генератора отчетов
- [ ] Настройка экспорта в различные форматы

## Этап 3: Google Ads бот (4 недели)

### 3.1 Базовая функциональность
- [ ] Подключение к API Google Ads
- [ ] Сбор базовой статистики
- [ ] Сохранение данных в БД

### 3.2 Аналитические функции
- [ ] Анализ эффективности кампаний
- [ ] Расчет ключевых метрик
- [ ] Выявление проблемных мест

### 3.3 Оптимизация
- [ ] Автоматическая корректировка ставок
- [ ] Оптимизация бюджетов
- [ ] A/B тестирование

## Этап 4: Instagram Ads бот (4 недели)

### 4.1 Базовая функциональность
- [ ] Подключение к API Instagram
- [ ] Сбор статистики по постам и stories
- [ ] Сохранение данных в БД

### 4.2 Аналитические функции
- [ ] Анализ эффективности постов
- [ ] Анализ аудитории
- [ ] Определение лучшего времени публикации

### 4.3 Оптимизация
- [ ] Автоматическое планирование постов
- [ ] Оптимизация таргетинга
- [ ] Рекомендации по контенту

## Этап 5: Система мониторинга (2 недели)

### 5.1 Алерты
- [ ] Мониторинг расходов
- [ ] Отслеживание аномалий
- [ ] Система уведомлений

### 5.2 Дашборды
- [ ] Создание общего дашборда
- [ ] Дашборд по Google Ads
- [ ] Дашборд по Instagram

## Этап 6: Интеграция с SEO ботом (3 недели)

### 6.1 Объединение данных
- [ ] Создание общего хранилища
- [ ] Унификация метрик
- [ ] Создание единого интерфейса

### 6.2 Кросс-канальная аналитика
- [ ] Сравнение эффективности каналов
- [ ] Анализ взаимного влияния
- [ ] Рекомендации по распределению бюджета

## Этап 7: Тестирование и оптимизация (2 недели)

### 7.1 Тестирование
- [ ] Модульные тесты
- [ ] Интеграционные тесты
- [ ] Нагрузочное тестирование

### 7.2 Оптимизация
- [ ] Оптимизация производительности
- [ ] Оптимизация использования API
- [ ] Оптимизация базы данных

## Этап 8: Документация и развертывание (2 недели)

### 8.1 Документация
- [ ] API документация
- [ ] Руководство пользователя
- [ ] Руководство разработчика

### 8.2 Развертывание
- [ ] Настройка CI/CD
- [ ] Подготовка production окружения
- [ ] Мониторинг production

## Технические требования

### База данных
- PostgreSQL 13+
- TimescaleDB для временных рядов
- Партиционирование по дате

### API и интеграции
- Google Ads API v13
- Instagram Graph API
- OAuth 2.0 аутентификация

### Мониторинг
- Prometheus + Grafana
- ELK Stack для логов
- Sentry для ошибок

### Безопасность
- Шифрование данных
- Ролевой доступ
- Аудит действий

## Метрики успеха проекта

1. Технические метрики:
   - Время отклика API < 200ms
   - Доступность системы > 99.9%
   - Корректность данных > 99.99%

2. Бизнес метрики:
   - Снижение стоимости конверсии на 20%
   - Увеличение ROI рекламных кампаний на 30%
   - Экономия времени на управление рекламой на 70%

## Риски и их митигация

1. Технические риски:
   - Ограничения API: Использование очередей и кэширования
   - Проблемы с данными: Валидация и очистка данных

2. Бизнес риски:
   - Изменения в API платформ: Модульная архитектура
   - Масштабируемость: Микросервисная архитектура

## Дальнейшее развитие

1. Новые платформы:
   - Facebook Ads
   - TikTok Ads
   - YouTube Ads

2. Дополнительные функции:
   - Предиктивная аналитика
   - Автоматическая генерация креативов
   - Интеграция с CRM системами

## Структура проекта

```bash
marketing_bots/
├── src/                      # Исходный код
│   ├── core/                 # Ядро системы
│   │   ├── abstract_bot.py   # Базовый класс для всех ботов
│   │   ├── metrics.py        # Общие метрики и KPI
│   │   └── exceptions.py     # Пользовательские исключения
│   │
│   ├── google_ads/          # Google Ads бот
│   │   ├── collector.py     # Сбор данных
│   │   ├── analyzer.py      # Анализ данных
│   │   ├── optimizer.py     # Оптимизация кампаний
│   │   └── report.py        # Генерация отчетов
│   │
│   ├── instagram_ads/       # Instagram Ads бот
│   │   ├── collector.py     # Сбор данных
│   │   ├── analyzer.py      # Анализ данных
│   │   ├── optimizer.py     # Оптимизация постов
│   │   └── report.py        # Генерация отчетов
│   │
│   ├── common/             # Общие компоненты
│   │   ├── data_processor.py # Обработка данных
│   │   ├── db_handler.py    # Работа с БД
│   │   └── utils.py         # Вспомогательные функции
│   │
│   └── monitoring/         # Мониторинг и алерты
│       ├── alerts.py       # Система оповещений
│       └── dashboard.py    # Дашборды
│
├── scripts/                # Скрипты
│   ├── setup/             # Настройка
│   │   ├── init_db.py     # Инициализация БД
│   │   ├── setup_google_ads.py
│   │   └── setup_instagram_ads.py
│   │
│   ├── analysis/          # Анализ данных
│   │   ├── performance.sql    # Анализ эффективности
│   │   ├── trends.sql        # Анализ трендов
│   │   └── compare.sql       # Сравнение каналов
│   │
│   └── utils/             # Утилиты
│       ├── check_apis.py  # Проверка API
│       └── validate_data.py # Валидация данных
│
├── tests/                 # Тесты
│   ├── unit/             # Модульные тесты
│   │   ├── test_google_ads.py
│   │   └── test_instagram_ads.py
│   │
│   ├── integration/      # Интеграционные тесты
│   │   ├── test_collectors.py
│   │   └── test_analyzers.py
│   │
│   └── fixtures/         # Тестовые данные
│       ├── google_ads_data.json
│       └── instagram_data.json
│
├── database/             # База данных
│   ├── migrations/       # Миграции
│   │   ├── 001_initial.sql
│   │   └── 002_metrics.sql
│   │
│   ├── google_ads_schema.sql
│   └── instagram_ads_schema.sql
│
├── config/              # Конфигурация
│   ├── google_ads.yaml
│   ├── instagram_ads.yaml
│   └── logging.yaml
│
├── docs/               # Документация
│   ├── api/           # API документация
│   │   ├── google_ads.md
│   │   └── instagram_ads.md
│   │
│   ├── setup/        # Инструкции по установке
│   │   ├── google_ads_setup.md
│   │   └── instagram_setup.md
│   │
│   └── development/  # Документация для разработчиков
│       ├── architecture.md
│       └── contributing.md
│
├── logs/              # Логи
│   ├── error.log
│   └── debug.log
│
├── .env.example      # Пример переменных окружения
├── requirements.txt  # Зависимости
├── setup.py         # Установка проекта
└── README.md        # Основная документация

## Описание ключевых компонентов

### Core (Ядро)
- `abstract_bot.py`: Базовый класс с общим интерфейсом для всех рекламных ботов
- `metrics.py`: Определение и расчет общих метрик (CTR, CPC, ROI и т.д.)
- `exceptions.py`: Пользовательские исключения для обработки ошибок

### Google Ads и Instagram Ads
- `collector.py`: Сбор данных через API
- `analyzer.py`: Анализ эффективности рекламных кампаний
- `optimizer.py`: Автоматическая оптимизация на основе правил
- `report.py`: Генерация отчетов и визуализаций

### Common (Общие компоненты)
- `data_processor.py`: Обработка и трансформация данных
- `db_handler.py`: Работа с базой данных
- `utils.py`: Общие утилиты

### Monitoring (Мониторинг)
- `alerts.py`: Система оповещений о проблемах
- `dashboard.py`: Визуализация метрик в реальном времени

### Database (База данных)
Основные таблицы:
```sql
-- Кампании
CREATE TABLE campaigns (
    id SERIAL PRIMARY KEY,
    platform TEXT,
    campaign_id TEXT,
    name TEXT,
    status TEXT,
    budget DECIMAL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Метрики
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    campaign_id TEXT,
    platform TEXT,
    metric_name TEXT,
    metric_value DECIMAL,
    date DATE
);

-- Оптимизации
CREATE TABLE optimizations (
    id SERIAL PRIMARY KEY,
    campaign_id TEXT,
    action_type TEXT,
    old_value TEXT,
    new_value TEXT,
    reason TEXT,
    created_at TIMESTAMP
);
```

### Config (Конфигурация)
Пример конфигурации:
```yaml
google_ads:
  client_id: ${GOOGLE_CLIENT_ID}
  client_secret: ${GOOGLE_CLIENT_SECRET}
  developer_token: ${GOOGLE_DEVELOPER_TOKEN}
  refresh_token: ${GOOGLE_REFRESH_TOKEN}
  customer_id: ${GOOGLE_CUSTOMER_ID}

instagram_ads:
  access_token: ${INSTAGRAM_ACCESS_TOKEN}
  app_secret: ${INSTAGRAM_APP_SECRET}
  account_id: ${INSTAGRAM_ACCOUNT_ID}

database:
  host: ${DB_HOST}
  port: ${DB_PORT}
  name: ${DB_NAME}
  user: ${DB_USER}
  password: ${DB_PASSWORD}

monitoring:
  alert_threshold: 0.2
  check_interval: 300

```

## Итерация 3: Интеграция рекламных систем

### 1. Подготовка к интеграции Google Ads (2 недели)

#### 1.1 Настройка API и авторизации
```python
# src/google_ads/auth.py
class GoogleAdsAuth:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        
    def get_client(self) -> GoogleAdsClient:
        return GoogleAdsClient.load_from_dict(self.config)
```

**Почему это важно:**
- Безопасная работа с API ключами
- Централизованное управление доступом
- Возможность легко обновлять токены

#### 1.2 Сбор базовых метрик
```sql
-- database/migrations/003_google_ads_metrics.sql
CREATE TABLE google_ads_metrics (
    id SERIAL PRIMARY KEY,
    campaign_id TEXT,
    impressions INTEGER,
    clicks INTEGER,
    cost DECIMAL,
    conversions INTEGER,
    date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Почему это важно:**
- Отслеживание эффективности кампаний
- Историческая аналитика
- Основа для оптимизации

### 2. Интеграция с Instagram Ads (2 недели)

#### 2.1 Настройка Instagram Graph API
```python
# src/instagram_ads/collector.py
class InstagramAdsCollector:
    def get_campaign_insights(self, campaign_id: str, date_range: tuple) -> dict:
        """
        Получение статистики по рекламной кампании
        """
        return self.api.get_insights(
            campaign_id,
            fields=['impressions', 'reach', 'clicks', 'spend'],
            date_range={'since': date_range[0], 'until': date_range[1]}
        )
```

**Почему это важно:**
- Автоматизация сбора данных
- Единый интерфейс для всех метрик
- Возможность сравнения с другими каналами

#### 2.2 Анализ эффективности постов
```python
# src/instagram_ads/analyzer.py
class PostAnalyzer:
    def analyze_engagement(self, post_data: dict) -> dict:
        """
        Анализ вовлеченности аудитории
        """
        return {
            'engagement_rate': (post_data['likes'] + post_data['comments']) / post_data['reach'],
            'cost_per_engagement': post_data['spend'] / (post_data['likes'] + post_data['comments'])
        }
```

**Почему это важно:**
- Оптимизация контента
- Улучшение таргетинга
- Снижение стоимости конверсии

### 3. Объединение данных (2 недели)

#### 3.1 Создание единого хранилища
```sql
-- database/migrations/004_unified_metrics.sql
CREATE TABLE unified_metrics (
    id SERIAL PRIMARY KEY,
    platform TEXT,  -- google_ads, instagram, organic
    source_id TEXT,
    metric_type TEXT,
    metric_value DECIMAL,
    date DATE,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Индексы для быстрого поиска
CREATE INDEX idx_unified_metrics_platform ON unified_metrics(platform);
CREATE INDEX idx_unified_metrics_date ON unified_metrics(date);
```

**Почему это важно:**
- Единый источник данных для анализа
- Упрощение сравнения каналов
- Оптимизация запросов

#### 3.2 Кросс-канальная аналитика
```python
# src/analytics/cross_channel.py
class CrossChannelAnalyzer:
    def compare_channels(self, start_date: str, end_date: str) -> dict:
        """
        Сравнение эффективности разных каналов
        """
        return {
            'cpc_comparison': self._get_cpc_by_channel(),
            'conversion_rates': self._get_conversion_rates(),
            'roi_analysis': self._calculate_roi_by_channel()
        }
    
    def _calculate_roi_by_channel(self) -> dict:
        """
        ROI для каждого канала
        """
        query = """
        SELECT 
            platform,
            SUM(CASE WHEN metric_type = 'revenue' THEN metric_value ELSE 0 END) as revenue,
            SUM(CASE WHEN metric_type = 'cost' THEN metric_value ELSE 0 END) as cost,
            (SUM(CASE WHEN metric_type = 'revenue' THEN metric_value ELSE 0 END) - 
             SUM(CASE WHEN metric_type = 'cost' THEN metric_value ELSE 0 END)) / 
             NULLIF(SUM(CASE WHEN metric_type = 'cost' THEN metric_value ELSE 0 END), 0) as roi
        FROM unified_metrics
        GROUP BY platform
        """
        return self.db.execute(query)
```

**Почему это важно:**
- Оптимальное распределение бюджета
- Выявление наиболее эффективных каналов
- Обоснование маркетинговых решений

### 4. Оптимизация и автоматизация (2 недели)

#### 4.1 Автоматическая корректировка бюджетов
```python
# src/optimization/budget_optimizer.py
class BudgetOptimizer:
    def optimize_budgets(self, performance_data: dict) -> dict:
        """
        Перераспределение бюджетов на основе ROI
        """
        recommendations = {}
        for channel, metrics in performance_data.items():
            if metrics['roi'] > self.threshold:
                recommendations[channel] = {
                    'action': 'increase_budget',
                    'amount': self._calculate_optimal_increase(metrics)
                }
        return recommendations
```

**Почему это важно:**
- Максимизация ROI
- Автоматизация рутинных задач
- Быстрая реакция на изменения

#### 4.2 Система уведомлений
```python
# src/monitoring/alerts.py
class PerformanceAlert:
    def check_metrics(self) -> list:
        """
        Проверка метрик и генерация алертов
        """
        alerts = []
        metrics = self._get_current_metrics()
        
        for metric in metrics:
            if self._is_anomaly(metric):
                alerts.append({
                    'type': 'performance_drop',
                    'metric': metric['name'],
                    'value': metric['value'],
                    'threshold': metric['threshold'],
                    'channel': metric['channel']
                })
        
        return alerts
```

**Почему это важно:**
- Быстрое обнаружение проблем
- Предотвращение потерь трафика
- Контроль качества рекламных кампаний

## Ожидаемые результаты итерации:

1. **Технические:**
   - Полная интеграция с Google Ads и Instagram Ads
   - Единая система метрик и аналитики
   - Автоматизированная оптимизация

2. **Бизнес:**
   - Снижение стоимости привлечения клиента на 25%
   - Увеличение ROI рекламных кампаний на 30%
   - Сокращение времени на управление рекламой на 70%

## Метрики успеха:

1. **Количественные:**
   - Время сбора данных < 5 минут
   - Точность прогнозов > 85%
   - Автоматизация > 90% рутинных задач

2. **Качественные:**
   - Удобство использования системы
   - Понятность отчетов
   - Надежность работы интеграций

## План Итерации 3: Расширение функционала

## 1. ML-модели для анализа данных (2 недели)

### 1.1 Прогнозирование трафика
```python
# src/ml/traffic_predictor.py
class TrafficPredictor:
    def __init__(self):
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True
        )
    
    def predict_traffic(self, historical_data: pd.DataFrame, days_ahead: int = 30) -> pd.DataFrame:
        """
        Прогноз трафика на основе исторических данных
        """
        self.model.fit(historical_data)
        future = self.model.make_future_dataframe(periods=days_ahead)
        forecast = self.model.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
```

**Почему это важно:**
- Планирование ресурсов и контента
- Раннее выявление проблем
- Оптимизация маркетинговых кампаний

### 1.2 Выявление сезонности
```python
# src/ml/seasonality_analyzer.py
class SeasonalityAnalyzer:
    def analyze_seasonality(self, data: pd.DataFrame) -> dict:
        """
        Анализ сезонных паттернов в данных
        """
        decomposition = seasonal_decompose(
            data['traffic'],
            period=7,  # недельная сезонность
            model='additive'
        )
        return {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid
        }
```

**Почему это важно:**
- Оптимизация контент-стратегии
- Планирование акций и кампаний
- Улучшение прогнозов

### 1.3 Определение аномалий
```python
# src/ml/anomaly_detector.py
class AnomalyDetector:
    def detect_anomalies(self, metrics: pd.DataFrame) -> pd.DataFrame:
        """
        Поиск аномалий в метриках
        """
        isolation_forest = IsolationForest(contamination=0.1)
        metrics['is_anomaly'] = isolation_forest.fit_predict(metrics[['clicks', 'impressions', 'ctr']])
        return metrics[metrics['is_anomaly'] == -1]
```

**Почему это важно:**
- Быстрое обнаружение проблем
- Предотвращение потерь трафика
- Улучшение качества данных

## 2. Интеграции (2 недели)

### 2.1 Google Analytics
```python
# src/integrations/ga_collector.py
class GoogleAnalyticsCollector:
    def get_traffic_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Получение данных о трафике из Google Analytics
        """
        return self.analytics.reports().batchGet(
            body={
                'reportRequests': [{
                    'viewId': self.view_id,
                    'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                    'metrics': [{'expression': 'ga:users'}, {'expression': 'ga:sessions'}],
                    'dimensions': [{'name': 'ga:date'}]
                }]
            }
        ).execute()
```

### 2.2 Яндекс.Метрика
```python
# src/integrations/ym_collector.py
class YandexMetrikaCollector:
    def get_search_data(self, start_date: str, end_date: str) -> dict:
        """
        Получение данных из Яндекс.Метрики
        """
        return self.client.stats().get(
            metrics="ym:s:users,ym:s:visits,ym:s:bounceRate",
            dimensions="ym:s:date",
            date1=start_date,
            date2=end_date,
            group="day"
        )
```

### 2.3 Ahrefs API
```python
# src/integrations/ahrefs_collector.py
class AhrefsCollector:
    def get_competitors_data(self, domain: str) -> dict:
        """
        Получение данных о конкурентах
        """
        return self.client.reference_domains_by_type_new(
            target=domain,
            limit=1000,
            mode='domain',
            order_by='domain_rating:desc'
        )
```

## 3. Визуализация (2 недели)

### 3.1 Дашборды
```python
# src/visualization/dashboard_generator.py
class DashboardGenerator:
    def create_overview_dashboard(self, data: dict) -> str:
        """
        Создание общего дашборда
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Трафик', 'Позиции', 'CTR', 'Конверсии')
        )
        
        # Добавление графиков
        fig.add_trace(go.Scatter(x=data['dates'], y=data['traffic']), row=1, col=1)
        fig.add_trace(go.Scatter(x=data['dates'], y=data['positions']), row=1, col=2)
        fig.add_trace(go.Scatter(x=data['dates'], y=data['ctr']), row=2, col=1)
        fig.add_trace(go.Scatter(x=data['dates'], y=data['conversions']), row=2, col=2)
        
        return fig.to_html()
```

### 3.2 Экспорт данных
```python
# src/export/data_exporter.py
class DataExporter:
    def export_to_sheets(self, data: pd.DataFrame, sheet_id: str) -> None:
        """
        Экспорт данных в Google Sheets
        """
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json', scope
        )
        gc = gspread.authorize(credentials)
        worksheet = gc.open_by_key(sheet_id).sheet1
        worksheet.update([data.columns.values.tolist()] + data.values.tolist())
```

## Ожидаемые результаты:

1. **ML и аналитика:**
   - Точность прогнозов трафика > 85%
   - Выявление сезонных паттернов
   - Автоматическое определение аномалий

2. **Интеграции:**
   - Единая система данных из всех источников
   - Автоматическая синхронизация
   - Кросс-платформенная аналитика

3. **Визуализация:**
   - Интерактивные дашборды
   - Автоматическая генерация отчетов
   - Экспорт в разные форматы

## Метрики успеха:

1. **Технические:**
   - Точность ML моделей > 85%
   - Время обработки данных < 5 минут
   - Доступность системы > 99%

2. **Бизнес:**
   - Увеличение точности прогнозов на 40%
   - Сокращение времени на анализ на 60%
   - Улучшение качества принятия решений

## План реализации аналитических функций

## 1. Анализ динамики позиций

### 1.1 Отслеживание изменений позиций
```python
# src/analytics/position_analyzer.py
class PositionAnalyzer:
    def analyze_position_changes(self, data: pd.DataFrame, period: str = '7d') -> pd.DataFrame:
        """
        Анализ изменений позиций за период
        Args:
            data: DataFrame с колонками [query, position, date]
            period: период для сравнения ('7d', '30d')
        Returns:
            DataFrame с изменениями позиций
        """
        current = data.groupby('query')['position'].last()
        previous = data.groupby('query')['position'].first()
        
        changes = pd.DataFrame({
            'query': current.index,
            'current_position': current.values,
            'previous_position': previous.values,
            'change': previous.values - current.values
        })
        
        return changes.sort_values('change', ascending=False)
```

**Подзадачи:**
- [ ] Реализовать сравнение позиций по периодам (7д, 30д)
- [ ] Добавить фильтрацию по значимым изменениям (>5 позиций)
- [ ] Создать группировку по URL и категориям
- [ ] Добавить визуализацию изменений

## 2. Анализ изменений CTR

### 2.1 Анализатор CTR
```python
# src/analytics/ctr_analyzer.py
class CTRAnalyzer:
    def analyze_ctr_changes(self, data: pd.DataFrame) -> dict:
        """
        Анализ изменений CTR с выявлением аномалий
        Args:
            data: DataFrame с колонками [query, ctr, impressions, clicks, date]
        Returns:
            dict с результатами анализа
        """
        results = {
            'declining_ctr': self._get_declining_queries(data),
            'improving_ctr': self._get_improving_queries(data),
            'anomalies': self._detect_ctr_anomalies(data)
        }
        
        # Добавляем рекомендации
        results['recommendations'] = self._generate_recommendations(results)
        return results
    
    def _get_declining_queries(self, data: pd.DataFrame) -> pd.DataFrame:
        """Поиск запросов с падающим CTR"""
        return data[data['ctr_change'] < -0.1].sort_values('impressions', ascending=False)
```

**Подзадачи:**
- [ ] Реализовать расчет изменений CTR по периодам
- [ ] Добавить выявление аномальных изменений
- [ ] Создать систему рекомендаций по улучшению CTR
- [ ] Реализовать сравнение с средним CTR по позициям

## 3. Анализ эффективности страниц

### 3.1 Анализатор страниц
```python
# src/analytics/page_analyzer.py
class PageAnalyzer:
    def analyze_page_performance(self, data: pd.DataFrame) -> dict:
        """
        Комплексный анализ эффективности страниц
        Args:
            data: DataFrame с данными о страницах
        Returns:
            dict с результатами анализа
        """
        return {
            'top_pages': self._get_top_performing_pages(data),
            'problematic_pages': self._get_problematic_pages(data),
            'growth_opportunities': self._find_growth_opportunities(data)
        }
    
    def _get_problematic_pages(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Поиск проблемных страниц по критериям:
        - Низкий CTR относительно позиции
        - Падение трафика
        - Потеря позиций по ключевым запросам
        """
        problems = pd.DataFrame()
        
        # Находим страницы с низким CTR для своей позиции
        avg_ctr_by_position = data.groupby('position')['ctr'].mean()
        data['expected_ctr'] = data['position'].map(avg_ctr_by_position)
        data['ctr_ratio'] = data['ctr'] / data['expected_ctr']
        
        problems = data[data['ctr_ratio'] < 0.7].copy()
        problems['problem_type'] = 'low_ctr'
        
        return problems
```

**Подзадачи:**
- [ ] Создать метрики эффективности страниц
- [ ] Реализовать поиск проблемных страниц
- [ ] Добавить анализ потенциала роста
- [ ] Создать рекомендации по оптимизации

## 4. Создание отчетов

### 4.1 Генератор отчетов
```python
# src/reporting/report_generator.py
class SEOReportGenerator:
    def generate_comprehensive_report(self, data: dict) -> str:
        """
        Создание полного отчета по SEO метрикам
        """
        report = {
            'top_queries': self._analyze_top_queries(data),
            'problematic_pages': self._analyze_problems(data),
            'growth_opportunities': self._analyze_opportunities(data),
            'recommendations': self._generate_recommendations(data)
        }
        
        return self._format_report(report)
    
    def _analyze_top_queries(self, data: dict) -> pd.DataFrame:
        """
        Анализ топ запросов по метрикам:
        - Трафик
        - Конверсии
        - Потенциал роста
        """
        queries = pd.DataFrame(data['queries'])
        return queries.nlargest(20, 'traffic').copy()
```

**Подзадачи:**
- [ ] Создать шаблоны отчетов для разных целей
- [ ] Реализовать автоматическую генерацию отчетов
- [ ] Добавить экспорт в разные форматы
- [ ] Создать систему уведомлений о важных изменениях

## Метрики успеха:

1. **Точность анализа:**
   - Точность определения проблемных страниц > 90%
   - Точность прогнозов изменения позиций > 80%
   - Релевантность рекомендаций > 85%

2. **Эффективность:**
   - Время генерации отчетов < 30 секунд
   - Полнота покрытия данных > 95%
   - Актуальность данных (задержка < 24 часа)

3. **Бизнес-результаты:**
   - Увеличение среднего CTR на 20%
   - Рост позиций по проблемным страницам на 30%
   - Сокращение времени на анализ на 60%
