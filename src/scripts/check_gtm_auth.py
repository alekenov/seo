"""
Скрипт для проверки учетных данных GTM
"""
import os
import sys
import logging

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db import SupabaseDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Проверяет учетные данные GTM в базе данных."""
    db = SupabaseDB()
    
    # Получаем учетные данные GTM
    gtm_creds = db.get_credentials('gtm')
    logger.info(f"GTM учетные данные: {gtm_creds}")

if __name__ == '__main__':
    main()
