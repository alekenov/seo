#!/usr/bin/env python3
"""
Скрипт для отправки еженедельного отчета по SEO метрикам.
Запускается по расписанию через cron.
"""

import sys
import os
import logging
from datetime import datetime

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.reports.weekly_report import WeeklyReport
from src.utils.logger import setup_logger

# Настраиваем логирование
setup_logger('weekly_report')
logger = logging.getLogger(__name__)

def main():
    """Основная функция для отправки еженедельного отчета."""
    try:
        logger.info("Начинаем формирование еженедельного отчета")
        
        # Создаем объект отчета
        report = WeeklyReport()
        
        # Отправляем отчет
        success = report.send_weekly_report()
        
        if success:
            logger.info("Еженедельный отчет успешно отправлен")
        else:
            logger.error("Не удалось отправить еженедельный отчет")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Ошибка при отправке еженедельного отчета: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
