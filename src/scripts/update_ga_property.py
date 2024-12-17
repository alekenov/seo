#!/usr/bin/env python3
"""Скрипт для обновления Property ID в GA."""

import sys
import os
import argparse

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Обновление Property ID."""
    parser = argparse.ArgumentParser(description='Обновление Property ID для Google Analytics')
    parser.add_argument('property_id', help='Property ID (например, 123456789)')
    args = parser.parse_args()
    
    try:
        cm = CredentialsManager()
        
        # Получаем текущий Property ID
        current_id = cm.get_credential('ga', 'property_id')
        print(f"\nТекущий Property ID: {current_id}")
        
        # Обновляем Property ID
        cm.set_credential('ga', 'property_id', args.property_id, 'GA4 Property ID')
        print(f"\nProperty ID обновлен на: {args.property_id}")
            
    except Exception as e:
        logger.error(f"Ошибка при обновлении Property ID: {e}")
        raise

if __name__ == "__main__":
    main()
