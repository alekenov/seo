"""
Модуль для работы с базой данных Supabase
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from supabase import create_client, Client
import logging
from src.config.supabase_config import SUPABASE_URL, SUPABASE_SERVICE_ROLE, SupabaseConfig, DATABASE_URL

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """
    Создает и возвращает клиент Supabase
    
    Returns:
        Client: Клиент Supabase
    """
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)

class SupabaseDB:
    def __init__(self):
        """Инициализация подключения к базе данных."""
        config = SupabaseConfig()
        self.supabase: Client = create_client(config.url, config.key)
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True
        logger.info("Подключение к базе данных установлено")

    def execute(self, sql: str) -> dict:
        """
        Выполняет SQL запрос.
        
        Args:
            sql: SQL запрос для выполнения
            
        Returns:
            Результат выполнения запроса
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                if cur.description:
                    return cur.fetchall()
                return None
        except Exception as e:
            logger.error(f"Ошибка при выполнении SQL запроса: {str(e)}")
            raise

    def get_credentials(self, service_name: str) -> dict:
        """
        Получает учетные данные для сервиса из базы данных.
        
        Args:
            service_name: Имя сервиса
            
        Returns:
            Учетные данные сервиса
        """
        try:
            result = self.supabase.table('credentials').select('*').eq('service_name', service_name).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении учетных данных: {str(e)}")
            raise

    def __del__(self):
        """Закрываем соединение при удалении объекта."""
        if hasattr(self, 'conn'):
            self.conn.close()
