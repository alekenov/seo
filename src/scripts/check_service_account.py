#!/usr/bin/env python3
"""Скрипт для проверки Service Account."""

import sys
import os
import json

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Проверка Service Account."""
    try:
        # Путь к файлу Service Account
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
        sa_file = os.path.join(config_dir, 'thinking-field-415009-ddb12ae41a92.json')
        
        print(f"\nПроверяем Service Account в файле: {sa_file}")
        
        with open(sa_file, 'r') as f:
            sa_data = json.load(f)
            
        print("\nИнформация о Service Account:")
        print(f"Project ID: {sa_data.get('project_id')}")
        print(f"Client Email: {sa_data.get('client_email')}")
            
    except Exception as e:
        logger.error(f"Ошибка при проверке Service Account: {e}")
        raise

if __name__ == "__main__":
    main()
