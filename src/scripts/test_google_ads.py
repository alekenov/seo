"""Скрипт для проверки подключения к Google Ads API."""
import os
import sys

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.services.google_ads_service import GoogleAdsService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Основная функция."""
    try:
        # Инициализируем сервис
        ads_service = GoogleAdsService()
        
        # Получаем информацию об аккаунте
        account_info = ads_service.get_account_info()
        
        if account_info:
            logger.info("\n✅ Подключение к Google Ads API успешно установлено!")
            logger.info("\nИнформация об аккаунте:")
            logger.info(f"ID: {account_info['id']}")
            logger.info(f"Название: {account_info['name']}")
            logger.info(f"Валюта: {account_info['currency']}")
            logger.info(f"Часовой пояс: {account_info['timezone']}")
        else:
            logger.error("❌ Не удалось получить информацию об аккаунте")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке подключения: {str(e)}")

if __name__ == "__main__":
    main()
