"""
Конфигурация проекта.
"""
import os
from typing import Optional

from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class Config:
    """Конфигурация проекта."""
    
    def __init__(self):
        """Инициализация конфигурации."""
        self.creds = CredentialsManager()
        
        # Supabase
        self.SUPABASE_URL = self._get_credential('supabase', 'url')
        self.SUPABASE_KEY = self._get_credential('supabase', 'service_role')
        
        # Google Search Console
        self.GSC_SITE_URL = self._get_credential('gsc', 'site_url')
        self.GSC_CREDENTIALS_FILE = self._get_credential('gsc', 'credentials_file')
        self.GSC_PROJECT_ID = self._get_credential('gsc', 'project_id')
        
        # Telegram
        self.TELEGRAM_BOT_TOKEN = self._get_credential('telegram', 'bot_token')
        self.TELEGRAM_CHANNEL_ID = self._get_credential('telegram', 'channel_id')
    
    def _get_credential(self, service: str, key: str) -> Optional[str]:
        """Получение значения учетных данных.
        
        Args:
            service: Название сервиса
            key: Название ключа
            
        Returns:
            Значение если найдено, None в противном случае
        """
        value = self.creds.get_credential(service, key)
        if not value:
            logger.warning(f"Credential not found: {service}.{key}")
        return value

# Создаем глобальный экземпляр конфигурации
config = Config()
