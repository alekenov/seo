#!/usr/bin/env python3
"""
Скрипт для обновления учетных данных Supabase в таблице credentials
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
        
        # Supabase данные
        supabase_url = 'https://jvfjxlpplbyrafasobzl.supabase.co'
        anon_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2Zmp4bHBwbGJ5cmFmYXNvYnpsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM4OTg2NzUsImV4cCI6MjA0OTQ3NDY3NX0.1_tTwBDg1ibnlBbe6PyzID8CucrkQlXEUsA5dyNQ_g0'
        service_role = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2Zmp4bHBwbGJ5cmFmYXNvYnpsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzg5ODY3NSwiZXhwIjoyMDQ5NDc0Njc1fQ.sk2X5le3Rt3O0krvJREk0Cn4H8bI3V2rwx5Md2jg_SI'
        
        # Обновляем данные
        credentials.set_credential('supabase', 'url', supabase_url)
        logger.info("Supabase URL обновлен")
        
        credentials.set_credential('supabase', 'anon_key', anon_key)
        logger.info("Supabase Anon Key обновлен")
        
        credentials.set_credential('supabase', 'service_role', service_role)
        logger.info("Supabase Service Role обновлен")
        
        # Проверяем текущие значения
        logger.info("\nТекущие значения в базе:")
        logger.info(f"URL: {credentials.get_credential('supabase', 'url')}")
        logger.info(f"Anon Key: {credentials.get_credential('supabase', 'anon_key')[:30]}...")
        logger.info(f"Service Role: {credentials.get_credential('supabase', 'service_role')[:30]}...")
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении учетных данных: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
