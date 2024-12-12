"""Менеджер учетных данных."""
import json
import psycopg2
from datetime import datetime
from typing import Optional, Dict, Any

from src.config.supabase_config import DATABASE_URL
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class CredentialsManager:
    """Управление учетными данными в базе данных."""
    
    def __init__(self):
        """Инициализация менеджера учетных данных."""
        self.db_url = DATABASE_URL
    
    def _get_connection(self):
        """Получение подключения к базе данных."""
        return psycopg2.connect(self.db_url)
    
    def save_credentials(self, service: str, credentials_data: Dict[str, Any]) -> bool:
        """Сохранение учетных данных в базу.
        
        Args:
            service: Название сервиса (например, 'gsc' для Google Search Console)
            credentials_data: Данные учетной записи для сохранения
            
        Returns:
            True если успешно, False в противном случае
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Проверяем существование учетных данных
                    cur.execute(
                        "SELECT id FROM credentials WHERE service = %s",
                        (service,)
                    )
                    result = cur.fetchone()
                    
                    if result:
                        # Обновляем существующие учетные данные
                        cur.execute(
                            """
                            UPDATE credentials 
                            SET credentials_data = %s, updated_at = CURRENT_TIMESTAMP 
                            WHERE service = %s
                            """,
                            (json.dumps(credentials_data), service)
                        )
                    else:
                        # Создаем новые учетные данные
                        cur.execute(
                            """
                            INSERT INTO credentials (service, credentials_data) 
                            VALUES (%s, %s)
                            """,
                            (service, json.dumps(credentials_data))
                        )
                    
                    conn.commit()
            
            logger.info(f"Credentials saved for service: {service}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving credentials for {service}: {str(e)}")
            return False
    
    def load_credentials(self, service: str) -> Optional[Dict[str, Any]]:
        """Загрузка учетных данных из базы.
        
        Args:
            service: Название сервиса
            
        Returns:
            Данные учетной записи если найдены, None в противном случае
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT credentials_data FROM credentials WHERE service = %s",
                        (service,)
                    )
                    result = cur.fetchone()
                    
                    if not result:
                        return None
                    
                    credentials_data = result[0]
                    if isinstance(credentials_data, str):
                        credentials_data = json.loads(credentials_data)
                        
                    logger.info(f"Credentials loaded for service: {service}")
                    return credentials_data
            
        except Exception as e:
            logger.error(f"Error loading credentials for {service}: {str(e)}")
            return None
    
    def delete_credentials(self, service: str) -> bool:
        """Удаление учетных данных из базы.
        
        Args:
            service: Название сервиса
            
        Returns:
            True если успешно, False в противном случае
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM credentials WHERE service = %s",
                        (service,)
                    )
                    conn.commit()
            
            logger.info(f"Credentials deleted for service: {service}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting credentials for {service}: {str(e)}")
            return False
