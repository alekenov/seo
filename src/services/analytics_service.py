"""Сервис для работы с Google Analytics API."""
import json
from typing import Dict, List, Optional
from datetime import datetime

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class AnalyticsService:
    """Сервис для работы с Google Analytics API."""
    
    def __init__(self, credentials_dict: Dict, property_id: str):
        """Инициализация сервиса.
        
        Args:
            credentials_dict: Словарь с учетными данными сервисного аккаунта
            property_id: ID свойства GA4
        """
        self.property_id = property_id
        self._init_client(credentials_dict)
        
    def _init_client(self, credentials_dict: Dict):
        """Инициализация клиента GA4."""
        try:
            # Создаем учетные данные из сервисного аккаунта
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/analytics.readonly']
            )
            
            # Создаем клиента
            self.client = BetaAnalyticsDataClient(credentials=credentials)
            logger.info("Google Analytics клиент успешно инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации GA4 клиента: {e}")
            raise
            
    def get_report(
        self,
        start_date: datetime,
        end_date: datetime,
        metrics: List[str],
        dimensions: Optional[List[str]] = None
    ) -> Dict:
        """Получение отчета из Google Analytics.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            metrics: Список метрик (например, ['sessions', 'pageviews'])
            dimensions: Список измерений (например, ['date', 'pageTitle'])
            
        Returns:
            Dict с данными отчета
        """
        try:
            # Подготавливаем запрос
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d')
                )],
                metrics=[Metric(name=metric) for metric in metrics],
                dimensions=[Dimension(name=dim) for dim in (dimensions or [])]
            )
            
            # Выполняем запрос
            response = self.client.run_report(request)
            
            # Преобразуем ответ в словарь
            result = {
                'dimensions': dimensions or [],
                'metrics': metrics,
                'rows': []
            }
            
            for row in response.rows:
                row_data = {}
                
                # Добавляем значения измерений
                if dimensions:
                    for i, dimension in enumerate(dimensions):
                        row_data[dimension] = row.dimension_values[i].value
                        
                # Добавляем значения метрик
                for i, metric in enumerate(metrics):
                    row_data[metric] = row.metric_values[i].value
                    
                result['rows'].append(row_data)
                
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при получении отчета из GA4: {e}")
            raise
