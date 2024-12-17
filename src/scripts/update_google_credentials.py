#!/usr/bin/env python3
"""
Скрипт для обновления учетных данных Google сервисов в Supabase
"""
import logging
import os
import sys

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.credentials_manager import CredentialsManager

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        credentials = CredentialsManager()
        
        # 1. GSC Site URL
        gsc_site = 'sc-domain:cvety.kz'
        credentials.set_credential('gsc', 'site', gsc_site)
        logger.info(f"GSC site URL обновлен: {gsc_site}")
        
        # 2. Путь к файлу сервисного аккаунта
        service_account_file = 'dashbords-373217-20faafe15e3f.json'
        credentials.set_credential('google', 'service_account_file', service_account_file)
        logger.info(f"Путь к файлу сервисного аккаунта обновлен: {service_account_file}")
        
        # Проверяем текущие значения
        logger.info("\nТекущие значения в базе:")
        logger.info(f"GSC Site: {credentials.get_credential('gsc', 'site')}")
        logger.info(f"Service Account File: {credentials.get_credential('google', 'service_account_file')}")
        logger.info(f"GA Property ID: {credentials.get_credential('ga', 'property_id')}")
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении учетных данных: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
