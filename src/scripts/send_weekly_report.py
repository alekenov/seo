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

# Настраиваем логирование с максимальным уровнем детализации
logger = setup_logger('weekly_report')
logger.setLevel(logging.DEBUG)

def main():
    """Основная функция для отправки еженедельного отчета."""
    try:
        logger.info("Начинаем формирование еженедельного отчета")
        
        # Создаем объект отчета
        report = WeeklyReport()
        logger.debug("WeeklyReport объект создан")
        
        # Получаем данные для отчета
        logger.debug("Получаем данные для сравнения")
        data = report.get_comparison_data()
        logger.debug(f"Получены данные: {len(data['queries'])} запросов, {len(data['categories'])} категорий")
        
        # Форматируем отчет
        logger.debug("Форматируем отчет")
        report_text, images = report.format_comparison_report(data)
        logger.debug(f"Отчет отформатирован, получено {len(images)} изображений")
        
        # Отправляем текст отчета
        logger.debug("Отправляем текст отчета")
        report.telegram.send_message(report_text)
        logger.debug("Текст отчета отправлен")
        
        # Отправляем графики
        logger.debug("Отправляем графики")
        for i, image in enumerate(images, 1):
            logger.debug(f"Отправляем график {i}/{len(images)}")
            report.telegram.send_photo(image)
            
        logger.info("Еженедельный отчет успешно отправлен")
        return True
            
    except Exception as e:
        logger.error(f"Ошибка при отправке еженедельного отчета: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    main()
