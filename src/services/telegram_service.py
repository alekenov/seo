"""Сервис для работы с Telegram API."""

import asyncio
from typing import Optional
import nest_asyncio

from telegram import Bot
from telegram.constants import ParseMode

from src.utils.credentials_manager import CredentialsManager

# Включаем поддержку вложенных циклов событий
nest_asyncio.apply()


class TelegramService:
    """Класс для работы с Telegram API."""
    
    def __init__(self, bot_token: Optional[str] = None):
        """Инициализация сервиса Telegram."""
        self.credentials = CredentialsManager()
        self.bot_token = bot_token
        self._init_bot()
        self.loop = asyncio.get_event_loop()
        
    def _init_bot(self):
        """Инициализация бота."""
        if not self.bot_token:
            creds = self.credentials.load_credentials('telegram')
            self.bot_token = creds['bot_token']
        
        self.bot = Bot(self.bot_token)
        
    async def _send_message_async(self, chat_id: str, text: str, parse_mode: Optional[str] = None):
        """Асинхронная отправка сообщения."""
        await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode
        )
        
    def send_message(self, chat_id: str, text: str, parse_mode: Optional[str] = None):
        """Отправка сообщения."""
        self.loop.run_until_complete(self._send_message_async(chat_id, text, parse_mode))

    async def _send_image_async(self, chat_id: str, image_path: str, caption: Optional[str] = None):
        """Асинхронная отправка изображения."""
        with open(image_path, 'rb') as photo:
            await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode=ParseMode.HTML
            )
        
    def send_image(self, chat_id: str, image_path: str, caption: Optional[str] = None):
        """Отправка изображения."""
        self.loop.run_until_complete(self._send_image_async(chat_id, image_path, caption))
        
    async def _send_report_async(self, chat_id: str, text: str, image_paths: list[str]):
        """Асинхронная отправка отчета с изображениями."""
        # Отправляем текст
        await self._send_message_async(chat_id, text, parse_mode='HTML')
        
        # Отправляем изображения
        for image_path in image_paths:
            await self._send_image_async(chat_id, image_path)
            
    def send_report(self, chat_id: str, text: str, image_paths: list[str]):
        """Отправка отчета с изображениями."""
        self.loop.run_until_complete(
            self._send_report_async(chat_id, text, image_paths)
        )
