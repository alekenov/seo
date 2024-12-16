"""Сервис для работы с Google Ads API."""
import os
import json
import yaml
from typing import Optional, Dict, Any
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class GoogleAdsService:
    """Сервис для работы с Google Ads API."""
    
    def __init__(self):
        """Инициализация сервиса."""
        self.creds = CredentialsManager()
        self.client = self._initialize_client()
        
    def _initialize_client(self) -> Optional[GoogleAdsClient]:
        """Инициализация клиента Google Ads.
        
        Returns:
            GoogleAdsClient если успешно, None в противном случае
        """
        try:
            # Получаем учетные данные
            service_account_file = self.creds.get_credential('google_ads', 'service_account_file')
            developer_token = self.creds.get_credential('google_ads', 'developer_token')
            
            # Путь к файлу сервисного аккаунта
            config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
            service_account_path = os.path.join(config_dir, service_account_file)
            
            # Читаем содержимое файла сервисного аккаунта
            with open(service_account_path, 'r') as f:
                service_account_info = json.load(f)
            
            # Создаем временный yaml файл с конфигурацией
            config = {
                "developer_token": developer_token,
                "use_proto_plus": True,
                "json_key_file_path": service_account_path
            }
            
            config_path = os.path.join(config_dir, "google-ads.yaml")
            with open(config_path, "w") as f:
                yaml.dump(config, f)
            
            return GoogleAdsClient.load_from_storage(config_path)
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации клиента Google Ads: {str(e)}")
            return None
            
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Получение информации об аккаунте.
        
        Returns:
            Словарь с информацией об аккаунте если успешно, None в противном случае
        """
        try:
            if not self.client:
                raise Exception("Клиент Google Ads не инициализирован")
                
            customer_id = self.creds.get_credential('google_ads', 'customer_id')
            
            # Создаем сервис
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Формируем запрос
            query = """
                SELECT
                    customer.id,
                    customer.descriptive_name,
                    customer.currency_code,
                    customer.time_zone
                FROM customer
                LIMIT 1
            """
            
            # Выполняем запрос
            response = ga_service.search(customer_id=customer_id, query=query)
            
            # Обрабатываем результат
            for row in response:
                customer = row.customer
                return {
                    "id": customer.id,
                    "name": customer.descriptive_name,
                    "currency": customer.currency_code,
                    "timezone": customer.time_zone
                }
                
            return None
            
        except GoogleAdsException as ex:
            logger.error(f"Ошибка запроса к Google Ads API: {ex}")
            for error in ex.failure.errors:
                logger.error(f"\tError with message: {error.message}")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        logger.error(f"\t\tOn field: {field_path_element.field_name}")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации об аккаунте: {str(e)}")
            return None
