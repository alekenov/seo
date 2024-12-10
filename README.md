# SEO Data Collector

Инструмент для автоматизированного сбора SEO-метрик из Google Search Console.

## Структура проекта

```
seo-collector/
├── src/
│   ├── collectors/         # Коллекторы данных
│   ├── models/            # Модели данных
│   └── utils/             # Утилиты
├── data/
│   ├── raw/              # Сырые данные
│   └── processed/        # Обработанные данные
├── config/
│   ├── credentials.json  # Креды для Google API
│   └── settings.yaml     # Настройки проекта
└── requirements.txt      # Зависимости
```

## Установка

1. Клонируйте репозиторий
2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   # или
   venv\Scripts\activate  # для Windows
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Настройка

1. Создайте проект в Google Cloud Console
2. Включите Google Search Console API
3. Создайте credentials.json и поместите его в папку config/
4. Настройте параметры в config/settings.yaml

## Использование

[Будет добавлено позже]

## Разработка

[Будет добавлено позже]
