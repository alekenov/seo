from src.services.gtm_service import GTMService
from datetime import datetime
from src.database.db import SupabaseDB
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ga4_measurement_id(db):
    """Получить Measurement ID из базы данных"""
    try:
        credentials = db.get_credentials('ga4')
        if not credentials:
            raise ValueError("Учетные данные GA4 не найдены в базе данных")
        measurement_id = credentials.get('credentials', {}).get('measurement_id')
        if not measurement_id:
            raise ValueError("Measurement ID не найден в учетных данных GA4")
        return measurement_id
    except Exception as e:
        logger.error(f"Ошибка при получении Measurement ID: {str(e)}")
        raise

def get_or_create_variable(gtm, variable_data):
    """Получить существующую или создать новую переменную"""
    if gtm.variable_exists(variable_data['name']):
        logger.info(f"Переменная {variable_data['name']} уже существует")
        return True
    try:
        gtm.create_custom_variable(variable_data)
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании переменной {variable_data['name']}: {str(e)}")
        return False

def get_or_create_trigger(gtm, trigger_data):
    """Получить существующий или создать новый триггер"""
    if gtm.trigger_exists(trigger_data['name']):
        logger.info(f"Триггер {trigger_data['name']} уже существует")
        return True
    try:
        gtm.create_custom_trigger(trigger_data)
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании триггера {trigger_data['name']}: {str(e)}")
        return False

def get_or_create_tag(gtm, tag_data):
    """Получить существующий или создать новый тег"""
    if gtm.tag_exists(tag_data['name']):
        logger.info(f"Тег {tag_data['name']} уже существует")
        return True
    try:
        gtm.create_custom_tag(tag_data)
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании тега {tag_data['name']}: {str(e)}")
        return False

def setup_file_downloads(gtm, measurement_id):
    """Настройка отслеживания файловых загрузок"""
    try:
        # Создаем переменную для расширения файла
        var_success = get_or_create_variable(gtm, {
            'name': 'Click URL Extension',
            'type': 'jsm',
            'parameter': [{
                'type': 'template',
                'key': 'javascript',
                'value': """function() {
              var url = {{Click URL}};
              return url.split('.').pop().toLowerCase();
            }"""
            }]
        })
        time.sleep(3)
        
        # Создаем триггер
        trigger_success = get_or_create_trigger(gtm, {
            'name': 'File Download',
            'type': 'CLICK',
            'filter': [{
                'type': 'CONTAINS',
                'parameter': [
                    {'type': 'template', 'key': 'arg0', 'value': '{{Click URL}}'},
                    {'type': 'template', 'key': 'arg1', 'value': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.rar'}
                ]
            }]
        })
        time.sleep(3)
        
        # Создаем тег GA4
        tag_data = {
            'name': 'GA4 - File Download',
            'type': 'gaawe',
            'parameter': [
                {
                    'type': 'TEMPLATE',
                    'key': 'measurementId',
                    'value': measurement_id
                },
                {
                    'type': 'TEMPLATE',
                    'key': 'eventName',
                    'value': 'file_download'
                },
                {
                    'type': 'LIST',
                    'key': 'eventParameters',
                    'list': [
                        {
                            'type': 'MAP',
                            'map': [
                                {'type': 'TEMPLATE', 'key': 'name', 'value': 'file_name'},
                                {'type': 'TEMPLATE', 'key': 'value', 'value': '{{Click URL}}'}
                            ]
                        },
                        {
                            'type': 'MAP',
                            'map': [
                                {'type': 'TEMPLATE', 'key': 'name', 'value': 'file_extension'},
                                {'type': 'TEMPLATE', 'key': 'value', 'value': '{{Click URL Extension}}'}
                            ]
                        }
                    ]
                },
                {
                    'type': 'BOOLEAN',
                    'key': 'sendEcommerceData',
                    'value': 'false'
                },
                {
                    'type': 'TEMPLATE',
                    'key': 'tagManagerUrl',
                    'value': '{{Page URL}}'
                }
            ],
            'firingTriggerId': [trigger_success['triggerId']] if isinstance(trigger_success, dict) else []
        }
        
        tag_success = get_or_create_tag(gtm, tag_data)
        
        if not tag_success:
            raise Exception("Ошибка при создании тега GA4 - File Download")
        
        logger.info("Отслеживание файловых загрузок настроено")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при настройке отслеживания файловых загрузок: {str(e)}")
        return False

def setup_outbound_links(gtm, measurement_id):
    """Настройка отслеживания внешних ссылок"""
    try:
        trigger_success = get_or_create_trigger(gtm, {
            'name': 'Outbound Link',
            'type': 'CLICK',
            'filter': [{
                'type': 'MATCH_REGEX',
                'parameter': [
                    {'type': 'template', 'key': 'arg0', 'value': '{{Click URL}}'},
                    {'type': 'template', 'key': 'arg1', 'value': '^https?://(?!.*{{Page Hostname}}).*$'}
                ]
            }]
        })
        time.sleep(3)
        
        tag_data = {
            'name': 'GA4 - Outbound Link',
            'type': 'gaawe',
            'parameter': [
                {
                    'type': 'TEMPLATE',
                    'key': 'measurementId',
                    'value': measurement_id
                },
                {
                    'type': 'TEMPLATE',
                    'key': 'eventName',
                    'value': 'click'
                },
                {
                    'type': 'LIST',
                    'key': 'eventParameters',
                    'list': [
                        {
                            'type': 'MAP',
                            'map': [
                                {'type': 'TEMPLATE', 'key': 'name', 'value': 'link_url'},
                                {'type': 'TEMPLATE', 'key': 'value', 'value': '{{Click URL}}'}
                            ]
                        },
                        {
                            'type': 'MAP',
                            'map': [
                                {'type': 'TEMPLATE', 'key': 'name', 'value': 'link_text'},
                                {'type': 'TEMPLATE', 'key': 'value', 'value': '{{Click Text}}'}
                            ]
                        }
                    ]
                },
                {
                    'type': 'BOOLEAN',
                    'key': 'sendEcommerceData',
                    'value': 'false'
                },
                {
                    'type': 'TEMPLATE',
                    'key': 'tagManagerUrl',
                    'value': '{{Page URL}}'
                }
            ],
            'firingTriggerId': [trigger_success['triggerId']] if isinstance(trigger_success, dict) else []
        }
        
        tag_success = get_or_create_tag(gtm, tag_data)
        
        logger.info("Отслеживание внешних ссылок настроено")
        return all([trigger_success, tag_success])
    except Exception as e:
        logger.error(f"Ошибка при настройке отслеживания ссылок: {str(e)}")
        return False

def setup_forms(gtm, measurement_id):
    """Настройка отслеживания форм"""
    try:
        trigger_success = get_or_create_trigger(gtm, {
            'name': 'Form Submission',
            'type': 'FORM_SUBMISSION',
            'waitForTags': {
                'type': 'template',
                'value': '2000'
            },
            'checkValidation': {
                'type': 'template',
                'value': 'true'
            }
        })
        time.sleep(3)
        
        tag_data = {
            'name': 'GA4 - Form Submission',
            'type': 'gaawe',
            'parameter': [
                {
                    'type': 'TEMPLATE',
                    'key': 'measurementId',
                    'value': measurement_id
                },
                {
                    'type': 'TEMPLATE',
                    'key': 'eventName',
                    'value': 'form_submission'
                },
                {
                    'type': 'LIST',
                    'key': 'eventParameters',
                    'list': [
                        {
                            'type': 'MAP',
                            'map': [
                                {'type': 'TEMPLATE', 'key': 'name', 'value': 'form_id'},
                                {'type': 'TEMPLATE', 'key': 'value', 'value': '{{Form ID}}'}
                            ]
                        },
                        {
                            'type': 'MAP',
                            'map': [
                                {'type': 'TEMPLATE', 'key': 'name', 'value': 'form_name'},
                                {'type': 'TEMPLATE', 'key': 'value', 'value': '{{Form Name}}'}
                            ]
                        }
                    ]
                },
                {
                    'type': 'BOOLEAN',
                    'key': 'sendEcommerceData',
                    'value': 'false'
                },
                {
                    'type': 'TEMPLATE',
                    'key': 'tagManagerUrl',
                    'value': '{{Page URL}}'
                }
            ],
            'firingTriggerId': [trigger_success['triggerId']] if isinstance(trigger_success, dict) else []
        }
        
        tag_success = get_or_create_tag(gtm, tag_data)
        
        logger.info("Отслеживание форм настроено")
        return all([trigger_success, tag_success])
    except Exception as e:
        logger.error(f"Ошибка при настройке отслеживания форм: {str(e)}")
        return False

def setup_time_on_page(gtm, measurement_id):
    """Настройка отслеживания времени на странице"""
    try:
        trigger_success = get_or_create_trigger(gtm, {
            'name': 'Time on Page - 30 seconds',
            'type': 'TIMER',
            'parameter': [
                {'type': 'template', 'key': 'interval', 'value': '30000'},
                {'type': 'template', 'key': 'limit', 'value': '1'}
            ]
        })
        time.sleep(3)
        
        tag_data = {
            'name': 'GA4 - Time on Page',
            'type': 'gaawe',
            'parameter': [
                {
                    'type': 'TEMPLATE',
                    'key': 'measurementId',
                    'value': measurement_id
                },
                {
                    'type': 'TEMPLATE',
                    'key': 'eventName',
                    'value': 'time_on_page'
                },
                {
                    'type': 'LIST',
                    'key': 'eventParameters',
                    'list': [
                        {
                            'type': 'MAP',
                            'map': [
                                {'type': 'TEMPLATE', 'key': 'name', 'value': 'time_value'},
                                {'type': 'TEMPLATE', 'key': 'value', 'value': '30'}
                            ]
                        }
                    ]
                },
                {
                    'type': 'BOOLEAN',
                    'key': 'sendEcommerceData',
                    'value': 'false'
                },
                {
                    'type': 'TEMPLATE',
                    'key': 'tagManagerUrl',
                    'value': '{{Page URL}}'
                }
            ],
            'firingTriggerId': [trigger_success['triggerId']] if isinstance(trigger_success, dict) else []
        }
        
        tag_success = get_or_create_tag(gtm, tag_data)
        
        logger.info("Отслеживание времени на странице настроено")
        return all([trigger_success, tag_success])
    except Exception as e:
        logger.error(f"Ошибка при настройке отслеживания времени: {str(e)}")
        return False

def retry_with_backoff(func, max_retries=3, initial_delay=30):
    """Выполнить функцию с повторными попытками и экспоненциальной задержкой"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "Quota exceeded" in str(e):
                delay = initial_delay * (2 ** attempt)
                logger.warning(f"Превышена квота API. Ожидание {delay} секунд...")
                time.sleep(delay)
                continue
            raise
    return func()

def setup_enhanced_measurement():
    """Настройка Enhanced Measurement в GTM"""
    try:
        db = SupabaseDB()
        gtm = GTMService(db)
        measurement_id = get_ga4_measurement_id(db)
        
        # Добавляем механизм повторных попыток для каждого компонента
        retry_with_backoff(lambda: setup_file_downloads(gtm, measurement_id))
        time.sleep(30)  # Увеличиваем базовую задержку до 30 секунд
        
        retry_with_backoff(lambda: setup_outbound_links(gtm, measurement_id))
        time.sleep(30)
        
        retry_with_backoff(lambda: setup_forms(gtm, measurement_id))
        time.sleep(30)
        
        retry_with_backoff(lambda: setup_time_on_page(gtm, measurement_id))
        
        logger.info("Настройка Enhanced Measurement завершена успешно")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке Enhanced Measurement: {str(e)}")
        raise

if __name__ == "__main__":
    setup_enhanced_measurement()
    
    print("""
Enhanced Measurement настроен! Теперь отслеживаются:

1. Загрузки файлов:
   - PDF, DOC, XLS, PPT, ZIP, RAR
   - Событие: file_download
   - Параметры: file_name, file_extension

2. Внешние ссылки:
   - Клики по ссылкам на другие сайты
   - Событие: click
   - Параметры: link_url, link_text

3. Отправка форм:
   - Все формы на сайте
   - Событие: form_submission
   - Параметры: form_id, form_name

4. Время на странице:
   - Триггер срабатывает через 30 секунд
   - Событие: time_on_page
   - Параметры: time_value

Проверьте в режиме предварительного просмотра GTM:
1. Скачайте любой документ
2. Кликните по внешней ссылке
3. Отправьте тестовую форму
4. Подождите 30 секунд на странице
    """)
