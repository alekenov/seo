"""Скрипт для запуска отправки отчетов по расписанию."""
import asyncio
import os
import sys
from datetime import datetime, time
import aioschedule as schedule
from dotenv import load_dotenv

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.scripts.send_daily_report import send_daily_report
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

async def run_scheduler():
    """Запуск планировщика задач."""
    # Отправляем отчет каждый день в 10:00
    schedule.every().day.at("10:00").do(send_daily_report)
    
    logger.info("Scheduler started. Reports will be sent daily at 10:00")
    
    while True:
        await schedule.run_pending()
        await asyncio.sleep(60)  # Проверяем каждую минуту

def main():
    """Main function."""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Запускаем планировщик
    asyncio.run(run_scheduler())

if __name__ == "__main__":
    main()
