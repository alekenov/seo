#!/usr/bin/env python3
"""Скрипт для проверки учетных данных GSC."""

import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.credentials_manager import CredentialsManager

def main():
    """Проверка учетных данных GSC."""
    cm = CredentialsManager()
    print('GSC credentials:')
    for key in ['client_id', 'client_secret', 'refresh_token', 'token_uri', 'site_url']:
        value = cm.get_credential('gsc', key)
        print(f'{key}: {"[SET]" if value else "[NOT SET]"}')

if __name__ == "__main__":
    main()
