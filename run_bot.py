"""Script to run Telegram bot."""
import os
import sys
from dotenv import load_dotenv

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.bot.telegram_bot import SEOBot
from src.utils.config import Config

def main():
    """Run the bot."""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Инициализируем конфигурацию
    config = Config()
    
    # Создаем и запускаем бот
    bot = SEOBot(config)
    bot.run()

if __name__ == "__main__":
    main()
