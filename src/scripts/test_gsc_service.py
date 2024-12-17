#!/usr/bin/env python3
"""Скрипт для проверки работы GSC сервиса."""

import sys
import os
from datetime import datetime, timedelta

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.gsc_service import GSCService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Проверка работы GSC сервиса."""
    try:
        # Инициализируем сервис
        gsc = GSCService()
        
        # Получаем данные за последние 7 дней
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Запрашиваем данные
        data = gsc.get_search_analytics(start_date, end_date)
        
        # Выводим результаты
        print("\nПолучены данные из GSC:")
        print(f"Количество строк: {len(data.get('rows', []))}")
        
        if data.get('rows'):
            row = data['rows'][0]
            print("\nПример данных (первая строка):")
            print(f"URL: {row['keys'][0]}")
            print(f"Запрос: {row['keys'][1]}")
            print(f"Показы: {row['impressions']}")
            print(f"Клики: {row['clicks']}")
            print(f"CTR: {row['ctr']:.2%}")
            print(f"Позиция: {row['position']:.1f}")
            
    except Exception as e:
        logger.error(f"Ошибка при тестировании GSC сервиса: {e}")
        raise

if __name__ == "__main__":
    main()
