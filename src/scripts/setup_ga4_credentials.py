from src.database.db import SupabaseDB
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_ga4_credentials():
    """Настройка учетных данных GA4 в базе данных"""
    try:
        db = SupabaseDB()
        
        # Создаем запись с учетными данными GA4
        credentials = {
            'service_name': 'ga4',
            'measurement_id': 'G-X0F3KBN3ZT',
            'api_secret': 'z5xGFFioQnymQzOjEKw8mw',
            'stream_id': '2151182987'
        }
        
        # Проверяем существование записи
        existing = db.get_credentials('ga4')
        if existing:
            logger.info("Учетные данные GA4 уже существуют в базе данных")
            return
        
        # Добавляем новую запись
        db.insert_credentials(credentials)
        logger.info("Учетные данные GA4 успешно добавлены в базу данных")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке учетных данных GA4: {str(e)}")
        raise

if __name__ == "__main__":
    setup_ga4_credentials()
