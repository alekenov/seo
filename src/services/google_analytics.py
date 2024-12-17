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
    OrderBy,
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
            # Получаем учетные данные из таблицы credentials
            ga_credentials = self.credentials_manager.get_credential('ga')
            
            if not ga_credentials:
                raise Exception("Не найдены учетные данные GA4")
                
            # Получаем property_id и путь к файлу сервисного аккаунта
            self.property_id = ga_credentials.get('property_id')
            service_account_path = ga_credentials.get('service_account_path')
            
            if not service_account_path or not self.property_id:
                raise Exception("Отсутствуют обязательные учетные данные GA4")
            
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

    def get_ecommerce_overview(self, start_date: str, end_date: str) -> Dict:
        """
        Получение общей статистики по электронной коммерции.
        
        Args:
            start_date: Начальная дата в формате YYYY-MM-DD
            end_date: Конечная дата в формате YYYY-MM-DD
            
        Returns:
            Dict с метриками:
            - total_revenue: Общая выручка
            - transactions: Количество транзакций
            - avg_order_value: Средний чек
        """
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            metrics=[
                Metric(name="totalRevenue"),  # Общая выручка
                Metric(name="transactions")    # Количество транзакций
            ]
        )
        
        response = self.client.run_report(request)
        
        # Получаем значения метрик
        metrics = response.rows[0].metric_values if response.rows else []
        
        # Вычисляем средний чек
        avg_order_value = 0
        if metrics and int(metrics[1].value) > 0:  # если есть транзакции
            avg_order_value = float(metrics[0].value) / int(metrics[1].value)
        
        return {
            'total_revenue': float(metrics[0].value) if metrics else 0,
            'transactions': int(metrics[1].value) if len(metrics) > 1 else 0,
            'avg_order_value': round(avg_order_value, 2)
        }

    def get_sales_by_source(self, start_date: str, end_date: str) -> dict:
        """
        Получение статистики продаж по источникам трафика.
        
        Args:
            start_date: Начальная дата в формате YYYY-MM-DD
            end_date: Конечная дата в формате YYYY-MM-DD
            
        Returns:
            dict: Словарь со статистикой по каждому источнику
        """
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="sessionSource"),
                Dimension(name="sessionMedium")
            ],
            metrics=[
                Metric(name="totalRevenue"),
                Metric(name="transactions"),
                Metric(name="purchaseRevenue"),
                Metric(name="purchaserConversionRate")
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            order_bys=[
                OrderBy(
                    metric=OrderBy.MetricOrderBy(
                        metric_name="totalRevenue"
                    ),
                    desc=True
                )
            ],
            limit=10
        )
        
        response = self.client.run_report(request)
        
        result = []
        for row in response.rows:
            source = row.dimension_values[0].value
            medium = row.dimension_values[1].value
            
            result.append({
                'source': f"{source}/{medium}",
                'revenue': float(row.metric_values[0].value),
                'transactions': int(row.metric_values[1].value),
                'conversion_rate': float(row.metric_values[3].value)
            })
            
        return result

    def get_product_performance(self, start_date: str, end_date: str, limit: int = 100) -> dict:
        """
        Получение статистики по товарам.
        
        Args:
            start_date: Начальная дата в формате YYYY-MM-DD
            end_date: Конечная дата в формате YYYY-MM-DD
            limit: Максимальное количество товаров
            
        Returns:
            dict: Словарь со статистикой по каждому товару
        """
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="itemName")
            ],
            metrics=[
                Metric(name="itemRevenue"),
                Metric(name="itemsPurchased")
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            order_bys=[
                OrderBy(
                    metric=OrderBy.MetricOrderBy(
                        metric_name="itemRevenue"
                    ),
                    desc=True
                )
            ],
            limit=limit
        )
        
        response = self.client.run_report(request)
        
        result = []
        for row in response.rows:
            result.append({
                'name': row.dimension_values[0].value,
                'revenue': float(row.metric_values[0].value),
                'quantity': int(row.metric_values[1].value)
            })
            
        return result

    def get_purchase_funnel(self, start_date: str, end_date: str) -> dict:
        """
        Получение статистики по воронке покупок.
        
        Args:
            start_date: Начальная дата в формате YYYY-MM-DD
            end_date: Конечная дата в формате YYYY-MM-DD
            
        Returns:
            dict: Словарь со статистикой по этапам воронки
        """
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="addToCarts"),
                Metric(name="transactions")
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
        )
        
        response = self.client.run_report(request)
        
        metrics = response.rows[0].metric_values if response.rows else []
        
        views = int(metrics[0].value) if metrics else 0
        carts = int(metrics[1].value) if len(metrics) > 1 else 0
        purchases = int(metrics[2].value) if len(metrics) > 2 else 0
        
        # Вычисляем конверсии
        cart_rate = (carts / views * 100) if views > 0 else 0
        purchase_rate = (purchases / views * 100) if views > 0 else 0
        cart_to_purchase = (purchases / carts * 100) if carts > 0 else 0
        
        return {
            'page_views': views,
            'add_to_carts': carts,
            'purchases': purchases,
            'cart_rate': round(cart_rate, 2),
            'purchase_rate': round(purchase_rate, 2),
            'cart_to_purchase_rate': round(cart_to_purchase, 2)
        }
