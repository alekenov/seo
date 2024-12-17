#!/usr/bin/env python3
"""Скрипт для просмотра списка сайтов в GSC."""

import sys
import os

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.gsc_service import GSCService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Просмотр списка сайтов в GSC."""
    try:
        gsc = GSCService()
        
        # Получаем список сайтов
        sites = gsc.service.sites().list().execute()
        
        print("\nДоступные сайты в GSC:")
        for site in sites.get('siteEntry', []):
            print(f"URL: {site['siteUrl']}")
            print(f"Разрешения: {site['permissionLevel']}")
            print(f"Статус: {site.get('siteVerificationState', 'Неизвестно')}")
            print("-" * 50)
            
    except Exception as e:
        logger.error(f"Ошибка при получении списка сайтов: {e}")
        raise

if __name__ == "__main__":
    main()
