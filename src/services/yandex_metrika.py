import requests
from datetime import datetime, timedelta
import pandas as pd
import json

class YandexMetrikaAPI:
    """
    Класс для работы с API Яндекс.Метрики
    """
    
    def __init__(self, token, counter_id):
        """
        Инициализация клиента API
        
        Args:
            token (str): OAuth-токен
            counter_id (int): ID счетчика Яндекс.Метрики
        """
        self.token = token
        self.counter_id = counter_id
        self.base_url = 'https://api-metrika.yandex.ru/stat/v1/data'
        
    def _make_request(self, params, format='json'):
        """
        Выполнение запроса к API
        
        Args:
            params (dict): Параметры запроса
            format (str): Формат ответа (json или csv)
        
        Returns:
            dict/str: Ответ от API
        """
        headers = {
            'Authorization': f'OAuth {self.token}',
            'Accept': 'application/json'
        }
        
        url = f"{self.base_url}.{format}"
        
        # Добавляем ID счетчика к параметрам
        params['id'] = self.counter_id
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        if format == 'json':
            return response.json()
        return response.text

    def get_traffic_sources(self, date1='7daysAgo', date2='today'):
        """
        Получение данных по источникам трафика
        
        Args:
            date1 (str): Начальная дата
            date2 (str): Конечная дата
        
        Returns:
            pd.DataFrame: Данные по источникам трафика
        """
        params = {
            'date1': date1,
            'date2': date2,
            'metrics': 'ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds',
            'dimensions': 'ym:s:trafficSource',
            'limit': 100
        }
        
        data = self._make_request(params)
        
        # Преобразуем данные в DataFrame
        rows = []
        for item in data['data']:
            row = {
                'source': item['dimensions'][0]['name'],
                'visits': item['metrics'][0],
                'users': item['metrics'][1],
                'bounce_rate': item['metrics'][2],
                'page_depth': item['metrics'][3],
                'avg_duration': item['metrics'][4]
            }
            rows.append(row)
            
        return pd.DataFrame(rows)

    def get_popular_pages(self, date1='7daysAgo', date2='today', limit=20):
        """
        Получение списка популярных страниц
        """
        params = {
            'date1': date1,
            'date2': date2,
            'metrics': 'ym:s:visits',
            'dimensions': 'ym:s:startURL',
            'limit': limit
        }
        
        data = self._make_request(params)
        
        rows = []
        for item in data['data']:
            row = {
                'url': item['dimensions'][0]['name'],
                'visits': item['metrics'][0]
            }
            rows.append(row)
            
        return pd.DataFrame(rows)

    def get_conversion_goals(self, date1='7daysAgo', date2='today', goal_id=None):
        """
        Получение данных по целям
        
        Args:
            date1 (str): Начальная дата
            date2 (str): Конечная дата
            goal_id (int): ID цели (если None, то все цели)
        
        Returns:
            pd.DataFrame: Данные по целям
        """
        metrics = ['ym:s:visits', 'ym:s:goal<goal_id>reaches', 'ym:s:goal<goal_id>conversionRate']
        if goal_id:
            metrics = [m.replace('<goal_id>', str(goal_id)) for m in metrics]
        
        params = {
            'date1': date1,
            'date2': date2,
            'metrics': ','.join(metrics),
            'dimensions': 'ym:s:date',
            'sort': 'ym:s:date'
        }
        
        data = self._make_request(params)
        
        rows = []
        for item in data['data']:
            row = {
                'date': item['dimensions'][0]['name'],
                'visits': item['metrics'][0],
                'conversions': item['metrics'][1],
                'conversion_rate': item['metrics'][2]
            }
            rows.append(row)
            
        return pd.DataFrame(rows)

    def get_search_phrases(self, date1='7daysAgo', date2='today', limit=100):
        """
        Получение поисковых фраз
        
        Args:
            date1 (str): Начальная дата
            date2 (str): Конечная дата
            limit (int): Количество фраз
        
        Returns:
            pd.DataFrame: Данные по поисковым фразам
        """
        params = {
            'date1': date1,
            'date2': date2,
            'metrics': 'ym:s:visits',
            'dimensions': 'ym:s:searchPhrase',
            'limit': limit
        }
        
        data = self._make_request(params)
        
        rows = []
        for item in data['data']:
            if item['dimensions'][0]['name']:  # Пропускаем пустые фразы
                row = {
                    'phrase': item['dimensions'][0]['name'],
                    'visits': item['metrics'][0]
                }
                rows.append(row)
                
        return pd.DataFrame(rows)

    def get_devices(self, date1='7daysAgo', date2='today'):
        """
        Получение данных по устройствам
        
        Args:
            date1 (str): Начальная дата
            date2 (str): Конечная дата
        
        Returns:
            pd.DataFrame: Данные по устройствам
        """
        params = {
            'date1': date1,
            'date2': date2,
            'metrics': 'ym:s:visits,ym:s:users,ym:s:bounceRate',
            'dimensions': 'ym:s:deviceCategory',
            'limit': 10
        }
        
        data = self._make_request(params)
        
        rows = []
        for item in data['data']:
            row = {
                'device': item['dimensions'][0]['name'],
                'visits': item['metrics'][0],
                'users': item['metrics'][1],
                'bounce_rate': item['metrics'][2]
            }
            rows.append(row)
            
        return pd.DataFrame(rows)

    def save_report(self, report_data, filename):
        """
        Сохранение отчета в файл
        
        Args:
            report_data (pd.DataFrame): Данные отчета
            filename (str): Имя файла
        """
        if filename.endswith('.csv'):
            report_data.to_csv(filename, index=False)
        elif filename.endswith('.xlsx'):
            report_data.to_excel(filename, index=False)
        elif filename.endswith('.json'):
            report_data.to_json(filename, orient='records', force_ascii=False)
        else:
            raise ValueError("Неподдерживаемый формат файла")

# Пример использования:
if __name__ == "__main__":
    # Инициализация клиента
    token = 'y0_AgAAAAAIQVdQAAzyygAAAAEcFYUiAACbs5T2SZBAtbCrBXrF7T-3NHSfVw'
    counter_id = 26416359
    
    metrika = YandexMetrikaAPI(token, counter_id)
    
    # Получение данных по источникам трафика
    traffic_sources = metrika.get_traffic_sources()
    print("\nИсточники трафика:")
    print(traffic_sources)
    
    # Получение популярных страниц
    popular_pages = metrika.get_popular_pages(limit=10)
    print("\nПопулярные страницы:")
    print(popular_pages)
    
    # Получение данных по конверсиям
    conversions = metrika.get_conversion_goals()
    print("\nКонверсии:")
    print(conversions)
    
    # Сохранение отчетов
    metrika.save_report(traffic_sources, 'reports/traffic_sources.csv')
    metrika.save_report(popular_pages, 'reports/popular_pages.xlsx')
    metrika.save_report(conversions, 'reports/conversions.json')
