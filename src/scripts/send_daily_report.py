"""Скрипт для отправки ежедневного отчета в Telegram канал."""
import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.analytics.report_generator import ReportGenerator
from src.bot.channel_manager import ChannelManager
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

async def send_daily_report():
    """Отправка ежедневного отчета в канал."""
    try:
        # Генерируем отчет
        report_generator = ReportGenerator()
        report_data = report_generator.generate_daily_report()
        
        # Инициализируем менеджер канала
        config = Config()
        channel_manager = ChannelManager(config)
        
        # Форматируем и отправляем отчет
        message = report_generator.format_report_message(report_data)
        success = await channel_manager.send_message(message)
        
        if success:
            logger.info("Daily report sent successfully")
        else:
            logger.error("Failed to send daily report")
            
    except Exception as e:
        logger.error(f"Error sending daily report: {e}")
        raise

def main():
    """Main function."""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Запускаем отправку отчета
    asyncio.run(send_daily_report())

if __name__ == "__main__":
    main()
