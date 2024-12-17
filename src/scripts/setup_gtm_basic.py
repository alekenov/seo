"""
Скрипт для настройки базового отслеживания в GTM:
- Page View (просмотр страницы)
- Click (клики по элементам)
- Scroll (прокрутка страницы)
"""

import logging
from src.services.gtm_service import GTMService
from src.database.db import SupabaseDB

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_entity_exists(gtm: GTMService, name: str, entity_type: str) -> bool:
    """
    Проверяет существование сущности (тега или триггера) по имени
    
    Args:
        gtm: Экземпляр GTMService
        name: Имя сущности
        entity_type: Тип сущности ('tag' или 'trigger')
        
    Returns:
        bool: True если сущность существует, False если нет
    """
    try:
        workspace_id = gtm.get_workspace_id()
        
        if entity_type == 'trigger':
            entities = gtm.service.accounts().containers().workspaces().triggers().list(
                parent=f'accounts/{gtm.account_id}/containers/{gtm.container_id}/workspaces/{workspace_id}'
            ).execute().get('trigger', [])
        else:
            entities = gtm.service.accounts().containers().workspaces().tags().list(
                parent=f'accounts/{gtm.account_id}/containers/{gtm.container_id}/workspaces/{workspace_id}'
            ).execute().get('tag', [])
            
        return any(e['name'] == name for e in entities)
        
    except Exception as e:
        logger.error(f"Ошибка при проверке существования {entity_type}: {str(e)}")
        return False

def create_page_view_tracking(gtm: GTMService):
    """Создание отслеживания просмотра страниц"""
    try:
        trigger_name = 'Page View - All Pages'
        tag_name = 'GA4 - Page View'
        
        # Проверяем существование триггера и тега
        if check_entity_exists(gtm, trigger_name, 'trigger'):
            logger.info(f"Триггер {trigger_name} уже существует")
            return
            
        if check_entity_exists(gtm, tag_name, 'tag'):
            logger.info(f"Тег {tag_name} уже существует")
            return
        
        # Создаем триггер для всех страниц
        trigger = {
            'name': trigger_name,
            'type': 'pageview'
        }
        
        workspace_id = gtm.get_workspace_id()
        trigger_result = gtm.service.accounts().containers().workspaces().triggers().create(
            parent=f'accounts/{gtm.account_id}/containers/{gtm.container_id}/workspaces/{workspace_id}',
            body=trigger
        ).execute()
        
        # Создаем тег для отправки события в GA4
        tag = {
            'name': tag_name,
            'type': 'gaawe',
            'parameter': [
                {
                    'type': 'template',
                    'key': 'eventName',
                    'value': 'page_view'
                }
            ],
            'firingTriggerId': [trigger_result['triggerId']],
            'tagFiringOption': 'oncePerEvent'
        }
        
        tag_result = gtm.service.accounts().containers().workspaces().tags().create(
            parent=f'accounts/{gtm.account_id}/containers/{gtm.container_id}/workspaces/{workspace_id}',
            body=tag
        ).execute()
        
        logger.info(f"Настроено отслеживание просмотра страниц: {tag_result['name']}")
        return tag_result
        
    except Exception as e:
        logger.error(f"Ошибка при настройке отслеживания просмотра страниц: {str(e)}")
        raise

def create_click_tracking(gtm: GTMService):
    """Создание отслеживания кликов"""
    try:
        trigger_name = 'Click - All Elements'
        tag_name = 'GA4 - Click'
        
        # Проверяем существование триггера и тега
        if check_entity_exists(gtm, trigger_name, 'trigger'):
            logger.info(f"Триггер {trigger_name} уже существует")
            return
            
        if check_entity_exists(gtm, tag_name, 'tag'):
            logger.info(f"Тег {tag_name} уже существует")
            return
        
        # Создаем триггер для всех кликов
        trigger = {
            'name': trigger_name,
            'type': 'click'
        }
        
        workspace_id = gtm.get_workspace_id()
        trigger_result = gtm.service.accounts().containers().workspaces().triggers().create(
            parent=f'accounts/{gtm.account_id}/containers/{gtm.container_id}/workspaces/{workspace_id}',
            body=trigger
        ).execute()
        
        # Создаем тег для отправки события в GA4
        tag = {
            'name': tag_name,
            'type': 'gaawe',
            'parameter': [
                {
                    'type': 'template',
                    'key': 'eventName',
                    'value': 'click'
                }
            ],
            'firingTriggerId': [trigger_result['triggerId']],
            'tagFiringOption': 'oncePerEvent'
        }
        
        tag_result = gtm.service.accounts().containers().workspaces().tags().create(
            parent=f'accounts/{gtm.account_id}/containers/{gtm.container_id}/workspaces/{workspace_id}',
            body=tag
        ).execute()
        
        logger.info(f"Настроено отслеживание кликов: {tag_result['name']}")
        return tag_result
        
    except Exception as e:
        logger.error(f"Ошибка при настройке отслеживания кликов: {str(e)}")
        raise

def create_scroll_tracking(gtm: GTMService):
    """Создание отслеживания прокрутки"""
    try:
        trigger_name = 'Scroll Depth'
        tag_name = 'GA4 - Scroll'
        
        # Проверяем существование триггера и тега
        if check_entity_exists(gtm, trigger_name, 'trigger'):
            logger.info(f"Триггер {trigger_name} уже существует")
            return
            
        if check_entity_exists(gtm, tag_name, 'tag'):
            logger.info(f"Тег {tag_name} уже существует")
            return
        
        # Создаем триггер для прокрутки
        trigger = {
            'name': trigger_name,
            'type': 'scrollDepth',
            'parameter': [
                {
                    'type': 'template',
                    'key': 'verticalThresholdUnits',
                    'value': 'PERCENT'
                },
                {
                    'type': 'template',
                    'key': 'verticalThresholds',
                    'value': '25,50,75,90'
                }
            ]
        }
        
        workspace_id = gtm.get_workspace_id()
        trigger_result = gtm.service.accounts().containers().workspaces().triggers().create(
            parent=f'accounts/{gtm.account_id}/containers/{gtm.container_id}/workspaces/{workspace_id}',
            body=trigger
        ).execute()
        
        # Создаем тег для отправки события в GA4
        tag = {
            'name': tag_name,
            'type': 'gaawe',
            'parameter': [
                {
                    'type': 'template',
                    'key': 'eventName',
                    'value': 'scroll'
                }
            ],
            'firingTriggerId': [trigger_result['triggerId']],
            'tagFiringOption': 'oncePerEvent'
        }
        
        tag_result = gtm.service.accounts().containers().workspaces().tags().create(
            parent=f'accounts/{gtm.account_id}/containers/{gtm.container_id}/workspaces/{workspace_id}',
            body=tag
        ).execute()
        
        logger.info(f"Настроено отслеживание прокрутки: {tag_result['name']}")
        return tag_result
        
    except Exception as e:
        logger.error(f"Ошибка при настройке отслеживания прокрутки: {str(e)}")
        raise

def main():
    """Основная функция для настройки базового отслеживания"""
    try:
        # Инициализируем сервис GTM
        gtm = GTMService(SupabaseDB())
        
        # Настраиваем отслеживание просмотра страниц
        create_page_view_tracking(gtm)
        
        # Настраиваем отслеживание кликов
        create_click_tracking(gtm)
        
        # Настраиваем отслеживание прокрутки
        create_scroll_tracking(gtm)
        
        # Публикуем изменения
        gtm.publish_workspace()
        
        logger.info("Базовое отслеживание успешно настроено")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке базового отслеживания: {str(e)}")
        raise

if __name__ == '__main__':
    main()
