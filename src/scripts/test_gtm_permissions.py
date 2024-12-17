import logging
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("\nПроверка доступов к GTM API...")
        
        # Путь к файлу сервисного аккаунта
        credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                      'dashbords-373217-20faafe15e3f.json')
        
        # Создаем учетные данные
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/tagmanager.edit.containers']
        )
        
        # Создаем сервис GTM
        service = build('tagmanager', 'v2', credentials=credentials)
        
        # Пробуем получить список аккаунтов
        accounts = service.accounts().list().execute()
        
        logger.info(f"Успешно получен список аккаунтов GTM: {accounts}")
        logger.info("Доступы к GTM API работают корректно!")
        
    except Exception as e:
        logger.error(f"Ошибка при проверке доступов к GTM: {str(e)}")
        raise

if __name__ == "__main__":
    main()
