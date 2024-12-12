"""Manager for Telegram channels."""
import os
from typing import Dict, Any, Optional
import asyncio

from telegram import Bot
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ChannelManager:
    """Manager for sending messages to Telegram channels."""
    
    def __init__(self, config: Config):
        """Initialize channel manager.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        
        # Получаем токен и ID канала из переменных окружения
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        self.channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        if not self.channel_id:
            raise ValueError("TELEGRAM_CHANNEL_ID not found in environment variables")
            
        self.bot = Bot(token=token)
    
    async def send_message(self, message: str, parse_mode: Optional[str] = "HTML") -> bool:
        """Send message to channel.
        
        Args:
            message: Message text
            parse_mode: Message parse mode (HTML/Markdown)
            
        Returns:
            bool: True if message was sent successfully
        """
        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"Message sent to channel {self.channel_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending message to channel: {e}")
            return False
    
    async def send_report(self, report_data: Dict[str, Any]) -> bool:
        """Send report to channel.
        
        Args:
            report_data: Report data
            
        Returns:
            bool: True if report was sent successfully
        """
        try:
            # Форматируем отчет
            message = self._format_report(report_data)
            return await self.send_message(message)
        except Exception as e:
            logger.error(f"Error sending report to channel: {e}")
            return False
    
    def _format_report(self, report_data: Dict[str, Any]) -> str:
        """Format report data as message.
        
        Args:
            report_data: Report data
            
        Returns:
            str: Formatted message
        """
        # TODO: Реализовать красивое форматирование отчета
        message = "📊 <b>Отчет по SEO позициям</b>\n\n"
        
        if "date" in report_data:
            message += f"📅 Дата: {report_data['date']}\n\n"
        
        if "summary" in report_data:
            message += "📈 <b>Основные показатели:</b>\n"
            for metric, value in report_data["summary"].items():
                message += f"• {metric}: {value}\n"
            message += "\n"
        
        if "changes" in report_data:
            message += "🔄 <b>Значимые изменения:</b>\n"
            for change in report_data["changes"]:
                message += f"• {change}\n"
        
        return message
