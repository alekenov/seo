"""Тесты для Telegram сервиса."""

import unittest
from unittest.mock import Mock, patch

from src.services.telegram_service import TelegramService


class TestTelegramService(unittest.TestCase):
    """Тесты для класса TelegramService."""
    
    def setUp(self):
        """Подготовка к тестам."""
        self.telegram = TelegramService()
        
    @patch('src.services.telegram_service.Bot')
    def test_send_message(self, mock_bot):
        """Тест отправки сообщения."""
        # Подготавливаем мок
        mock_bot_instance = Mock()
        mock_bot.return_value = mock_bot_instance
        
        # Тестируем успешную отправку
        test_message = "Тестовое сообщение"
        result = self.telegram.send_message_sync(test_message)
        
        # Проверяем что сообщение было отправлено
        self.assertTrue(result)
        mock_bot_instance.send_message.assert_called_once()
        
        # Проверяем параметры вызова
        call_args = mock_bot_instance.send_message.call_args
        self.assertEqual(call_args.kwargs['text'], test_message)
        
    @patch('src.services.telegram_service.Bot')
    def test_send_message_error(self, mock_bot):
        """Тест обработки ошибки при отправке сообщения."""
        # Подготавливаем мок с ошибкой
        mock_bot_instance = Mock()
        mock_bot_instance.send_message.side_effect = Exception("Test error")
        mock_bot.return_value = mock_bot_instance
        
        # Тестируем отправку
        result = self.telegram.send_message_sync("test")
        
        # Проверяем что метод вернул False
        self.assertFalse(result)
        
    @patch('src.services.telegram_service.Bot')
    def test_send_image(self, mock_bot):
        """Тест отправки изображения."""
        # Подготавливаем мок
        mock_bot_instance = Mock()
        mock_bot.return_value = mock_bot_instance
        
        # Тестируем отправку с подписью
        test_caption = "Тестовая подпись"
        with patch('builtins.open', unittest.mock.mock_open(read_data=b'test')):
            result = self.telegram.send_image_sync(
                "test.png",
                caption=test_caption
            )
        
        # Проверяем результат
        self.assertTrue(result)
        mock_bot_instance.send_photo.assert_called_once()
        
        # Проверяем параметры вызова
        call_args = mock_bot_instance.send_photo.call_args
        self.assertEqual(call_args.kwargs['caption'], test_caption)


if __name__ == '__main__':
    unittest.main()
