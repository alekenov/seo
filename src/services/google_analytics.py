"""
Модуль для работы с Google Analytics API
"""
import os
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account

class GoogleAnalytics:
    def __init__(self, property_id: str, credentials_path: str = None):
        """
        Инициализация клиента Google Analytics
        
        Args:
            property_id: ID свойства Google Analytics 4
            credentials_path: Путь к файлу с учетными данными (service account)
        """
        if not credentials_path:
            credentials_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'dashbords-373217-20faafe15e3f.json'
            )
            
        self.property_id = property_id
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        self.client = BetaAnalyticsDataClient(credentials=self.credentials)
        
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
