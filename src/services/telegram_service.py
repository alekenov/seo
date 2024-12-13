"""Сервис для работы с Telegram API."""

import asyncio
from typing import Optional

from telegram import Bot
from telegram.constants import ParseMode

from src.utils.credentials_manager import CredentialsManager


class TelegramService:
    """Класс для работы с Telegram API."""
    
    def __init__(self, bot_token: Optional[str] = None):
        """Инициализация сервиса Telegram."""
        self.credentials = CredentialsManager()
        self.bot_token = bot_token
        self._init_bot()
        
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
        asyncio.run(self._send_message_async(chat_id, text, parse_mode))

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
        asyncio.run(self._send_image_async(chat_id, image_path, caption))
