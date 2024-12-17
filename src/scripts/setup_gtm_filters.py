from src.services.gtm_service import GTMService
from datetime import datetime
from src.database.db import SupabaseDB
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_bot_filter():
    """Настройка фильтрации ботов и внутреннего трафика"""
    try:
        # Инициализация сервисов
        db = SupabaseDB()
        gtm = GTMService(db)
        
        # 1. Создаем переменную для определения ботов
        bot_variable = gtm.create_custom_variable({
            'name': 'Bot Detection',
            'type': 'jsm',
            'parameter': [{
                'type': 'template',
                'key': 'javascript',
                'value': """function() {
                  var botPatterns = [
                    'bot', 'crawler', 'spider', 'ping', 'nagios',
                    'slurp', 'facebookexternalhit', 'lighthouse',
                    'pagespeed', 'gtmetrix'
                  ];
                  
                  var userAgent = navigator.userAgent.toLowerCase();
                  for (var i = 0; i < botPatterns.length; i++) {
                    if (userAgent.indexOf(botPatterns[i]) !== -1) {
                      return true;
                    }
                  }
                  
                  return false;
                }"""
            }]
        })
        time.sleep(2)  # Ждем создания переменной
        
        # 2. Создаем переменную для определения внутреннего трафика
        internal_ip_variable = gtm.create_custom_variable({
            'name': 'Internal IP',
            'type': 'jsm',
            'parameter': [{
                'type': 'template',
                'key': 'javascript',
                'value': """function() {
                  var internalIPs = [
                    '127.0.0.1',
                    'localhost',
                    // Добавьте сюда IP-адреса вашей организации
                  ];
                  
                  return internalIPs.indexOf(window.location.hostname) !== -1;
                }"""
            }]
        })
        time.sleep(2)  # Ждем создания переменной
        
        # 3. Создаем триггер для исключения ботов
        bot_trigger = gtm.create_custom_trigger({
            'name': 'Bot Traffic',
            'type': 'customEvent',
            'customEventFilter': [{
                'type': 'equals',
                'parameter': [
                    {'type': 'template', 'key': 'arg0', 'value': '{{Bot Detection}}'},
                    {'type': 'template', 'key': 'arg1', 'value': 'true'}
                ]
            }]
        })
        time.sleep(2)  # Ждем создания триггера
        
        # 4. Создаем триггер для исключения внутреннего трафика
        internal_trigger = gtm.create_custom_trigger({
            'name': 'Internal Traffic',
            'type': 'customEvent',
            'customEventFilter': [{
                'type': 'equals',
                'parameter': [
                    {'type': 'template', 'key': 'arg0', 'value': '{{Internal IP}}'},
                    {'type': 'template', 'key': 'arg1', 'value': 'true'}
                ]
            }]
        })
        time.sleep(2)  # Ждем создания триггера
        
        # 5. Создаем блокирующий триггер
        blocking_trigger = gtm.create_custom_trigger({
            'name': 'Block Bot and Internal',
            'type': 'trigger_group',
            'parameter': [{
                'type': 'template',
                'key': 'conditions',
                'value': f'[{bot_trigger["triggerId"]}, {internal_trigger["triggerId"]}]'
            }]
        })
        time.sleep(2)  # Ждем создания триггера
        
        # 6. Обновляем все теги GA4, добавляя блокирующий триггер
        ga4_tags = gtm.list_tags()
        for tag in ga4_tags:
            if 'GA4' in tag['name']:
                tag['blockingTriggerId'] = [blocking_trigger['triggerId']]
                gtm.update_tag(tag)
                time.sleep(1)  # Ждем обновления тега
        
        # 7. Создаем новую версию и публикуем
        version_name = f"Version {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        gtm.create_version(version_name)
        gtm.publish_version(version_name)
        
        logger.info("Фильтры для ботов и внутреннего трафика успешно настроены")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке фильтров: {str(e)}")
        raise

if __name__ == "__main__":
    setup_bot_filter()
    
    print("""
Фильтры настроены! Для проверки:
1. Откройте GTM и убедитесь, что созданы:
   - Переменная 'Bot Detection'
   - Переменная 'Internal IP'
   - Триггер 'Bot Traffic'
   - Триггер 'Internal Traffic'
   - Триггер 'Block Bot and Internal'
   
2. Проверьте, что все теги GA4 используют блокирующий триггер

3. Протестируйте фильтрацию:
   - Используйте User-Agent Switcher для имитации бота
   - Проверьте с локального хоста
   - Проверьте с IP-адресов вашей организации
    """)
