"""Сервис для работы с Google Search Console API."""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class GSCService:
    """Класс для работы с Google Search Console API."""
    
    SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
    
    def __init__(self):
        """Инициализация сервиса GSC."""
        self.credentials_manager = CredentialsManager()
        self._init_service()
        
    def _init_service(self):
        """Инициализация подключения к GSC API."""
        try:
            # Получаем путь к файлу service account
            config_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / 'config'
            credentials_file = config_dir / 'dashbords-373217-20faafe15e3f.json'
            
            if not credentials_file.exists():
                # Если файл не в config, пробуем корневую директорию
                credentials_file = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / 'dashbords-373217-20faafe15e3f.json'
            
            if not credentials_file.exists():
                raise FileNotFoundError(f"Файл {credentials_file} не найден")
            
            # Создаем credentials из service account
            credentials = service_account.Credentials.from_service_account_file(
                str(credentials_file),
                scopes=self.SCOPES
            )
            
            # Создаем сервис
            self.service = build('searchconsole', 'v1', credentials=credentials)
            self.site_url = self.credentials_manager.get_credential('gsc', 'site_url')
            
            if not self.site_url:
                raise ValueError("URL сайта не найден в базе данных")
                
            logger.info("GSC service успешно инициализирован")
            
        except Exception as e:
            logger.error(f"Error initializing GSC service: {str(e)}")
            raise

    def get_search_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        dimensions: List[str] = None
    ) -> Dict:
        """
        Получение данных из Search Analytics.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            dimensions: Список измерений (page, query, date, device, country)
            
        Returns:
            Dict: Данные из Search Analytics
        """
        if dimensions is None:
            dimensions = ['page', 'query']
            
        body = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': dimensions,
            'rowLimit': 25000,  # Максимальное количество строк
            'startRow': 0
        }
        
        try:
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url,
                body=body
            ).execute()
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка при получении данных из GSC: {e}")
            raise

    def get_page_category(self, page_path: str) -> str:
        """
        Определяет категорию страницы по её URL.
        
        Args:
            page_path: Путь страницы
            
        Returns:
            str: Название категории
        """
        from src.reports.constants import PAGE_CATEGORIES
        for category_id, category_data in PAGE_CATEGORIES.items():
            if category_data['pattern'].match(page_path):
                return category_data['name']
        return PAGE_CATEGORIES['other']['name']
        
    def group_by_category(self, analytics_data: Dict) -> Dict[str, Dict]:
        """
        Группирует данные по категориям страниц.
        
        Args:
            analytics_data: Данные из Search Analytics
            
        Returns:
            Dict[str, Dict]: Данные, сгруппированные по категориям
        """
        from src.reports.constants import PAGE_CATEGORIES
        categories = {}
        
        # Инициализируем категории
        for category in PAGE_CATEGORIES.values():
            categories[category['name']] = {
                'impressions': 0,
                'clicks': 0,
                'ctr': 0,
                'position': 0,
                'pages_count': 0
            }
            
        # Группируем данные
        for row in analytics_data.get('rows', []):
            page_path = row['keys'][0]  # Первый ключ - URL страницы
            category = self.get_page_category(page_path)
            
            categories[category]['impressions'] += row['impressions']
            categories[category]['clicks'] += row['clicks']
            categories[category]['position'] += row['position'] * row['impressions']  # Взвешенная позиция
            categories[category]['pages_count'] += 1
            
        # Вычисляем средние значения
        for category_data in categories.values():
            if category_data['impressions'] > 0:
                category_data['position'] /= category_data['impressions']  # Средняя взвешенная позиция
                category_data['ctr'] = category_data['clicks'] / category_data['impressions']
                
        return categories
        
    def get_top_queries(
        self,
        analytics_data: Dict,
        limit: int = 10
    ) -> List[Dict]:
        """
        Получает топ поисковых запросов.
        
        Args:
            analytics_data: Данные из Search Analytics
            limit: Количество запросов в топе
            
        Returns:
            List[Dict]: Список топ запросов с метриками
        """
        queries = []
        
        for row in analytics_data.get('rows', []):
            query = row['keys'][1]  # Второй ключ - поисковый запрос
            queries.append({
                'query': query,
                'clicks': row['clicks'],
                'impressions': row['impressions'],
                'ctr': row['clicks'] / row['impressions'] if row['impressions'] > 0 else 0,
                'position': row['position']
            })
            
        # Сортируем по кликам
        queries.sort(key=lambda x: x['clicks'], reverse=True)
        
        return queries[:limit]
