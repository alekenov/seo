"""Тестирование подключения к Telegram."""
import asyncio
from telegram import Bot

async def main():
    """Основная функция."""
    bot_token = "7866766987:AAGobujkQh7C_hz1yfTfS53fVZo2_o9P8Pk"
    channel_id = "-1002331813144"
    
    print(f"Testing bot with token: {bot_token}")
    print(f"Channel ID: {channel_id}")
    
    bot = Bot(bot_token)
    
    try:
        # Пробуем получить информацию о боте
        me = await bot.get_me()
        print(f"Bot info: {me.to_dict()}")
        
        # Пробуем отправить сообщение
        message = await bot.send_message(
            chat_id=channel_id,
            text="Test message from SEO Bot"
        )
        print(f"Message sent: {message.to_dict()}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
if __name__ == '__main__':
    asyncio.run(main())
