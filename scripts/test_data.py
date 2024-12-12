"""
Тестовые данные для анализа.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_test_data(days=30, queries=100):
    """Генерация тестовых данных"""
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(days)]
    
    # Генерируем запросы
    base_queries = [
        "купить цветы",
        "доставка цветов",
        "букет роз",
        "свадебные букеты",
        "цветы недорого",
        "букет на день рождения",
        "композиция из цветов",
        "подарочный букет",
        "цветы в коробке",
        "букет пионов"
    ]
    
    # Генерируем URLs
    base_urls = [
        "https://flowers.com/",
        "https://flowers.com/roses",
        "https://flowers.com/bouquets",
        "https://flowers.com/gifts",
        "https://flowers.com/wedding"
    ]
    
    data = []
    for date in dates:
        for query in base_queries:
            # Базовые метрики
            position = max(1, min(100, np.random.normal(5, 2)))
            impressions = int(np.random.normal(1000, 200))
            ctr_base = 0.2 if position <= 3 else 0.1 if position <= 5 else 0.05
            ctr = max(0.01, min(0.5, np.random.normal(ctr_base, 0.02)))
            clicks = int(impressions * ctr)
            
            data.append({
                'date': date,
                'query': query,
                'url': np.random.choice(base_urls),
                'position': position,
                'impressions': impressions,
                'clicks': clicks
            })
    
    return pd.DataFrame(data)

# Создаем тестовые данные
df = generate_test_data()
print("\nПример сгенерированных данных:")
print(df.head())

# Сохраняем в CSV для анализа
df.to_csv('dataset/test_data.csv', index=False)
print("\nДанные сохранены в dataset/test_data.csv")
