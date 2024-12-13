"""Константы для модуля отчетов."""

# Категории страниц
PAGE_CATEGORIES = {
    'product': {
        'name': 'Товары',
        'pattern': r'^/product/'
    },
    'category': {
        'name': 'Категории',
        'pattern': r'^/category/'
    },
    'blog': {
        'name': 'Блог',
        'pattern': r'^/blog/'
    },
    'other': {
        'name': 'Прочее',
        'pattern': r'.*'
    }
}

# Метрики для отслеживания
TRACKED_METRICS = [
    'clicks',
    'impressions',
    'ctr',
    'position'
]

# Пороговые значения для уведомлений
ALERT_THRESHOLDS = {
    'position_drop': 5,  # Падение позиции более чем на 5 пунктов
    'ctr_drop': 0.2,    # Падение CTR более чем на 20%
    'traffic_drop': 0.3  # Падение трафика более чем на 30%
}

# Форматирование отчетов
REPORT_FORMATS = {
    'date': '%d.%m.%Y',
    'time': '%H:%M',
    'number': '{:,}',
    'percent': '{:.1%}',
    'position': '{:.1f}'
}

# Максимальное количество элементов в топах
TOP_LIMITS = {
    'queries': 5,
    'pages': 5,
    'categories': 10
}
