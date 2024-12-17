"""
Скрипт для создания переменных DataLayer для e-commerce данных в GTM:
- item_id
- item_name
- price
- quantity
- currency
"""

import logging
from src.services.gtm_service import GTMService
from src.database.db import SupabaseDB
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_variable_exists(gtm: GTMService, name: str) -> bool:
    """Проверяет существование переменной по имени"""
    try:
        workspace_id = gtm.get_workspace_id()
        variables = gtm.service.accounts().containers().workspaces().variables().list(
            parent=f'accounts/{gtm.account_id}/containers/{gtm.container_id}/workspaces/{workspace_id}'
        ).execute().get('variable', [])
        
        return any(v['name'] == name for v in variables)
        
    except Exception as e:
        logger.error(f"Ошибка при проверке существования переменной: {str(e)}")
        return False

def create_datalayer_variable(gtm: GTMService, name: str, key: str):
    """
    Создает переменную DataLayer
    
    Args:
        gtm: Экземпляр GTMService
        name: Имя переменной
        key: Ключ в DataLayer
    """
    try:
        if check_variable_exists(gtm, name):
            logger.info(f"Переменная {name} уже существует")
            return
            
        workspace_id = gtm.get_workspace_id()
        
        variable = {
            'name': name,
            'type': 'v',
            'parameter': [
                {
                    'type': 'template',
                    'key': 'name',
                    'value': key
                }
            ]
        }
        
        result = gtm.service.accounts().containers().workspaces().variables().create(
            parent=f'accounts/{gtm.account_id}/containers/{gtm.container_id}/workspaces/{workspace_id}',
            body=variable
        ).execute()
        
        logger.info(f"Создана переменная DataLayer: {result['name']}")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при создании переменной {name}: {str(e)}")
        raise

def main():
    """Основная функция для создания e-commerce переменных"""
    try:
        # Инициализируем сервис GTM
        gtm = GTMService(SupabaseDB())
        
        # Создаем только currency переменную
        time.sleep(60)  # Увеличиваем задержку до 1 минуты
        create_datalayer_variable(gtm, 'dlv - Currency', 'currency')
        
        # Публикуем изменения
        time.sleep(5)  # Небольшая задержка перед публикацией
        gtm.publish_workspace()
        
        logger.info("E-commerce переменные успешно настроены")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке e-commerce переменных: {str(e)}")
        raise

if __name__ == '__main__':
    main()
