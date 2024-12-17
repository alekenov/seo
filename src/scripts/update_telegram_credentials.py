#!/usr/bin/env python3
"""
Скрипт для обновления учетных данных Telegram в Supabase
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
        
        # Telegram данные
        bot_token = '7866766987:AAGobujkQh7C_hz1yfTfS53fVZo2_o9P8Pk'
        channel_id = '-1002331813144'
        
        # Обновляем данные
        credentials.set_credential('telegram', 'bot_token', bot_token)
        logger.info(f"Telegram bot token обновлен")
        
        credentials.set_credential('telegram', 'channel_id', channel_id)
        logger.info(f"Telegram channel ID обновлен")
        
        # Проверяем текущие значения
        logger.info("\nТекущие значения в базе:")
        logger.info(f"Bot Token: {credentials.get_credential('telegram', 'bot_token')}")
        logger.info(f"Channel ID: {credentials.get_credential('telegram', 'channel_id')}")
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении учетных данных: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
