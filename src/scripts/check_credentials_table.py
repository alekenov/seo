#!/usr/bin/env python3
"""Скрипт для проверки таблицы credentials."""

import sys
import os

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Проверка значений в таблице credentials."""
    try:
        cm = CredentialsManager()
        
        # Проверяем GSC credentials
        print("\nGSC credentials:")
        gsc_keys = ['site_url', 'client_id', 'client_secret', 'refresh_token']
        for key in gsc_keys:
            value = cm.get_credential('gsc', key)
            print(f"{key}: {value if key == 'site_url' else '[SET]' if value else '[NOT SET]'}")
            
    except Exception as e:
        logger.error(f"Ошибка при проверке credentials: {e}")
        raise

if __name__ == "__main__":
    main()
