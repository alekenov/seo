"""Менеджер учетных данных."""
import json
import os
import psycopg2
from datetime import datetime
from typing import Optional, Dict, Any

from src.config.supabase_config import DATABASE_URL
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class CredentialsManager:
    """Управление учетными данными."""
    
    def __init__(self):
        """Инициализация менеджера учетных данных."""
        self.db_url = DATABASE_URL
    
    def _get_connection(self):
        """Получение подключения к базе данных."""
        return psycopg2.connect(self.db_url)
    
    def _resolve_env_var(self, value: str) -> str:
        """Разрешает переменную окружения в значение.
        
        Args:
            value: Значение, возможно содержащее переменную окружения
            
        Returns:
            Разрешенное значение
        """
        if not value:
            return value
            
        # Если значение не начинается с ${ или не заканчивается на }, возвращаем как есть
        if not (value.startswith('${') and value.endswith('}')):
            return value
            
        # Получаем имя переменной окружения
        env_var = value[2:-1]  # Убираем ${ и }
        
        # Для GSC и Telegram не используем переменные окружения
        if env_var.startswith(('TELEGRAM_', 'GSC_')):
            return value[2:-1]  # Возвращаем значение без ${ и }
            
        # Для остальных пытаемся получить из окружения
        return os.getenv(env_var, value)
    
    def get_credential(self, service_name: str, field: str = None) -> Optional[Any]:
        """
        Получение учетных данных из базы.
        
        Args:
            service_name: Имя сервиса
            field: Поле в JSONB объекте credentials (если None, возвращает весь объект)
            
        Returns:
            Значение учетных данных или None если не найдено
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Получаем JSONB объект credentials
                    query = """
                        SELECT credentials 
                        FROM credentials 
                        WHERE service_name = %s
                    """
                    logger.info(f"Executing query: {query} with params: {service_name}")
                    
                    cur.execute(query, (service_name,))
                    
                    row = cur.fetchone()
                    
                    if not row:
                        logger.warning(f"Не найдены учетные данные для сервиса {service_name}")
                        return None
                        
                    credentials = row[0]  # JSONB объект
                    logger.info(f"Retrieved credentials for {service_name}: {credentials}")
                    
                    # Если поле не указано, возвращаем весь объект
                    if not field:
                        return credentials
                        
                    # Если поле указано, возвращаем его значение
                    value = credentials.get(field)
                    logger.info(f"Retrieved field {field} = {value}")
                    return value
                    
        except Exception as e:
            logger.error(f"Error getting credential for {service_name}.{field}: {str(e)}")
            return None
    
    def set_credential(self, service_name: str, key_name: str, key_value: str, description: Optional[str] = None) -> bool:
        """Сохранение значения учетных данных.
        
        Args:
            service_name: Название сервиса
            key_name: Название ключа
            key_value: Значение ключа
            description: Описание (опционально)
            
        Returns:
            True если успешно, False в противном случае
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO credentials (service_name, key_name, key_value, description)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (service_name, key_name) DO UPDATE
                        SET key_value = EXCLUDED.key_value,
                            description = EXCLUDED.description,
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        (service_name, key_name, key_value, description)
                    )
                    conn.commit()
                    
            logger.info(f"Credential saved: {service_name}.{key_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving credential for {service_name}.{key_name}: {str(e)}")
            return False
    
    def get_service_credentials(self, service_name: str) -> Dict[str, str]:
        """Получение всех учетных данных для сервиса.
        
        Args:
            service_name: Название сервиса
            
        Returns:
            Словарь с учетными данными
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT key_name, key_value 
                        FROM credentials 
                        WHERE service_name = %s
                        """,
                        (service_name,)
                    )
                    return {row[0]: self._resolve_env_var(row[1]) for row in cur.fetchall()}
                    
        except Exception as e:
            logger.error(f"Error getting credentials for service {service_name}: {str(e)}")
            return {}
            
    def load_credentials(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Загрузка всех учетных данных для сервиса.
        
        Args:
            service_name: Название сервиса
            
        Returns:
            Словарь с учетными данными если найдены, None в противном случае
        """
        try:
            creds = self.get_service_credentials(service_name)
            if not creds:
                logger.error(f"No credentials found for service: {service_name}")
                return None
                
            return creds
            
        except Exception as e:
            logger.error(f"Error loading credentials for {service_name}: {str(e)}")
            return None
