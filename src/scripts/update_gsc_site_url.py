#!/usr/bin/env python3
"""Скрипт для обновления URL сайта в GSC."""

import sys
import os
import argparse

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Обновление URL сайта."""
    parser = argparse.ArgumentParser(description='Обновление URL сайта в GSC')
    parser.add_argument('url', help='Новый URL сайта (например, https://example.com/)')
    args = parser.parse_args()
    
    try:
        cm = CredentialsManager()
        
        # Получаем текущий URL
        current_url = cm.get_credential('gsc', 'site_url')
        print(f"\nТекущий URL сайта: {current_url}")
        
        # Обновляем URL
        cm.set_credential('gsc', 'site_url', args.url, 'GSC site URL')
        print(f"\nURL сайта обновлен на: {args.url}")
            
    except Exception as e:
        logger.error(f"Ошибка при обновлении URL: {e}")
        raise

if __name__ == "__main__":
    main()
