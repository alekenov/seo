import logging
import json
from typing import Dict, Any
from src.database.db import get_supabase_client

logger = logging.getLogger(__name__)

class CredentialsManager:
    """
    Класс для управления учетными данными из Supabase
    """
    
    def __init__(self):
        """
        Инициализация менеджера учетных данных
        """
        self.supabase = get_supabase_client()
        self._credentials_cache = {}
        
    def get_credentials(self, service_name: str) -> Dict[str, Any]:
        """
        Получение учетных данных для указанного сервиса из Supabase
        
        Args:
            service_name: Название сервиса (например, 'gtm', 'ga4')
            
        Returns:
            Dict[str, Any]: Словарь с учетными данными
        """
        try:
            # Проверяем кэш
            if service_name in self._credentials_cache:
                return self._credentials_cache[service_name]
            
            # Получаем учетные данные из Supabase
            response = self.supabase.table('credentials') \
                .select('*') \
                .eq('service_name', service_name) \
                .execute()
            
            if not response.data:
                raise ValueError(f"Учетные данные для сервиса {service_name} не найдены")
            
            # Преобразуем список записей в словарь
            credentials = {}
            for record in response.data:
                key = record.get('key_name')
                value = record.get('key_value')
                if key and value:
                    credentials[key] = value
            
            # Сохраняем в кэш
            self._credentials_cache[service_name] = credentials
            
            return credentials
            
        except Exception as e:
            logger.error(f"Ошибка при получении учетных данных для {service_name}: {str(e)}")
            raise
