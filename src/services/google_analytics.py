"""
Модуль для работы с Google Analytics API
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account
from ..utils.credentials_manager import CredentialsManager

class GoogleAnalytics:
    """Класс для работы с Google Analytics API."""
    
    SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
    
    def __init__(self):
        """
        Инициализация клиента Google Analytics
        """
        self.credentials_manager = CredentialsManager()
        self._init_service()
    
    def _init_service(self):
        """Инициализация подключения к GA API."""
        try:
            # Получаем property_id из таблицы credentials
            self.property_id = self.credentials_manager.get_credential('ga', 'property_id')
            
            # Получаем путь к файлу service account
            service_account_path = self.credentials_manager.get_credential('ga', 'service_account_path')
            
            if not os.path.exists(service_account_path):
                raise FileNotFoundError(f"Файл {service_account_path} не найден")
            
            # Создаем credentials из service account
            self.credentials = service_account.Credentials.from_service_account_file(
                service_account_path,
                scopes=self.SCOPES
            )
            
            # Создаем клиент
            self.client = BetaAnalyticsDataClient(credentials=self.credentials)
            
        except Exception as e:
            raise Exception(f"Ошибка при инициализации GA API: {str(e)}")
        
    def get_today_metrics(self):
        """
        Получение метрик за сегодняшний день
        
        Returns:
            dict: Словарь с метриками
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="sessionSource"),
                Dimension(name="sessionMedium"),
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="engagedSessions"),
            ],
            date_ranges=[
                DateRange(
                    start_date=today,
                    end_date=today,
                ),
            ],
        )
        
        response = self.client.run_report(request)
        
        result = {}
        for row in response.rows:
            source = f"{row.dimension_values[0].value}/{row.dimension_values[1].value}"
            result[source] = {
                "sessions": row.metric_values[0].value,
                "active_users": row.metric_values[1].value,
                "engaged_sessions": row.metric_values[2].value,
            }
            
        return result
        
    def get_metrics_by_date_range(self, start_date: str, end_date: str):
        """
        Получение метрик за указанный период
        
        Args:
            start_date: Начальная дата в формате YYYY-MM-DD
            end_date: Конечная дата в формате YYYY-MM-DD
            
        Returns:
            dict: Словарь с метриками
        """
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="date"),
                Dimension(name="sessionSource"),
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="purchaseConversions"),
                Metric(name="revenue"),
            ],
            date_ranges=[
                DateRange(
                    start_date=start_date,
                    end_date=end_date,
                ),
            ],
        )
        
        response = self.client.run_report(request)
        
        result = {
            'start_date': start_date,
            'end_date': end_date,
            'data': []
        }
        
        for row in response.rows:
            data = {
                'date': row.dimension_values[0].value,
                'source': row.dimension_values[1].value,
                'visits': int(row.metric_values[0].value),
                'orders': int(row.metric_values[1].value),
                'revenue': float(row.metric_values[2].value),
            }
            data['conversion'] = (data['orders'] / data['visits'] * 100) if data['visits'] > 0 else 0
            data['average_check'] = (data['revenue'] / data['orders']) if data['orders'] > 0 else 0
            result['data'].append(data)
            
        return result
