"""
Сервис для работы с Google Tag Manager API.
"""
import os
import logging
from typing import Dict, List, Optional, Tuple
from google.oauth2 import service_account
from googleapiclient.discovery import build
from ..database.db import SupabaseDB
from ..utils.logger import setup_logger
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class GTMService:
    """Сервис для работы с Google Tag Manager API"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/tagmanager.edit.containers',
        'https://www.googleapis.com/auth/tagmanager.publish',
        'https://www.googleapis.com/auth/tagmanager.manage.accounts',
        'https://www.googleapis.com/auth/tagmanager.delete.containers',
        'https://www.googleapis.com/auth/tagmanager.edit.containerversions'
    ]
    
    def __init__(self, db: SupabaseDB):
        """
        Инициализация сервиса GTM
        
        Args:
            db: Экземпляр класса SupabaseDB
        """
        self.db = db
        try:
            # Получаем учетные данные GTM
            creds = self.get_credentials()
            if not all(creds):
                raise ValueError("Не все учетные данные GTM найдены")
                
            self.account_id, self.container_id, service_account_path = creds
            
            # Создаем путь к файлу сервисного аккаунта
            service_account_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                service_account_path
            )
            
            # Создаем учетные данные
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path,
                scopes=self.SCOPES
            )
            
            # Создаем сервис GTM
            self.service = build('tagmanager', 'v2', credentials=credentials)
            
            logger.info(f"GTM сервис инициализирован для аккаунта {self.account_id} и контейнера {self.container_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации GTM сервиса: {str(e)}")
            raise
    
    def get_credentials(self) -> tuple:
        """
        Получает учетные данные GTM из базы данных.
        
        Returns:
            tuple: (account_id, container_id, service_account_path)
        """
        try:
            result = self.db.get_credentials('gtm')
            if not result:
                raise Exception("Учетные данные GTM не найдены в базе данных")
                
            creds = result['credentials']
            return (
                creds['account_id'],
                creds['container_id'],
                creds['service_account_path']
            )
        except Exception as e:
            logger.error(f"Ошибка при получении учетных данных GTM: {str(e)}")
            raise
    
    def get_workspace_id(self) -> str:
        """
        Получение ID рабочей области (workspace).
        
        Returns:
            str: ID рабочей области
        """
        try:
            # Получаем список рабочих областей
            workspaces = self.service.accounts().containers().workspaces().list(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}'
            ).execute()
            
            # Берем ID первой рабочей области (обычно Default Workspace)
            if workspaces.get('workspace'):
                return workspaces['workspace'][0]['workspaceId']
            
            raise Exception("Рабочие области не найдены")
            
        except Exception as e:
            logger.error(f"Ошибка при получении workspace_id: {str(e)}")
            raise
    
    def list_workspaces(self) -> List[Dict]:
        """Получение списка рабочих областей."""
        try:
            workspaces = self.service.accounts().containers().workspaces().list(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}'
            ).execute()
            
            logger.info("Доступные рабочие области:")
            for workspace in workspaces.get('workspace', []):
                logger.info(f"ID: {workspace.get('workspaceId')}, Name: {workspace.get('name')}")
                
            return workspaces.get('workspace', [])
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка рабочих областей: {str(e)}")
            raise
    
    def get_tags(self) -> List[Dict]:
        """
        Получение списка всех тегов.
        
        Returns:
            List[Dict]: Список тегов
        """
        try:
            workspace_id = self.get_workspace_id()
            result = self.service.accounts().containers().workspaces().tags().list(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}'
            ).execute()
            
            return result.get('tag', [])
            
        except Exception as e:
            logger.error(f"Ошибка при получении тегов: {str(e)}")
            return []
    
    def get_triggers(self) -> List[Dict]:
        """
        Получение списка всех триггеров.
        
        Returns:
            List[Dict]: Список триггеров
        """
        try:
            workspace_id = self.get_workspace_id()
            result = self.service.accounts().containers().workspaces().triggers().list(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}'
            ).execute()
            
            return result.get('trigger', [])
            
        except Exception as e:
            logger.error(f"Ошибка при получении триггеров: {str(e)}")
            return []
    
    def get_variables(self) -> List[Dict]:
        """
        Получение списка всех переменных.
        
        Returns:
            List[Dict]: Список переменных
        """
        try:
            workspace_id = self.get_workspace_id()
            result = self.service.accounts().containers().workspaces().variables().list(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}'
            ).execute()
            
            return result.get('variable', [])
            
        except Exception as e:
            logger.error(f"Ошибка при получении переменных: {str(e)}")
            return []
    
    def analyze_container(self) -> Dict:
        """
        Анализ контейнера GTM: проверка тегов, триггеров и переменных.
        
        Returns:
            Dict: Результаты анализа
        """
        try:
            tags = self.get_tags()
            triggers = self.get_triggers()
            variables = self.get_variables()
            
            # Анализируем теги
            ga4_tags = [tag for tag in tags if 'google_analytics' in tag.get('type', '').lower()]
            event_tags = [tag for tag in tags if tag.get('type') == 'custom_event']
            
            # Анализируем триггеры
            page_view_triggers = [t for t in triggers if 'page' in t.get('type', '').lower()]
            event_triggers = [t for t in triggers if 'event' in t.get('type', '').lower()]
            
            # Анализируем переменные
            data_layer_vars = [v for v in variables if 'dataLayer' in v.get('type', '')]
            
            return {
                'summary': {
                    'total_tags': len(tags),
                    'total_triggers': len(triggers),
                    'total_variables': len(variables)
                },
                'tags': {
                    'ga4_tags': len(ga4_tags),
                    'event_tags': len(event_tags)
                },
                'triggers': {
                    'page_view': len(page_view_triggers),
                    'events': len(event_triggers)
                },
                'variables': {
                    'data_layer': len(data_layer_vars)
                }
            }
            
        except Exception as e:
            logger.error(f"Ошибка при анализе контейнера: {str(e)}")
            return {}

    def create_page_view_trigger(self) -> Dict:
        """
        Создание триггера для отслеживания просмотра страниц.
        
        Returns:
            Dict: Созданный триггер
        """
        try:
            workspace_id = self.get_workspace_id()
            trigger = {
                'name': 'DOM Ready',
                'type': 'domReady',
                'parameter': [
                    {
                        'type': 'BOOLEAN',
                        'key': 'supportDocumentWrite',
                        'value': 'false'
                    }
                ]
            }
            
            result = self.service.accounts().containers().workspaces().triggers().create(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=trigger
            ).execute()
            
            logger.info(f"Создан триггер DOM Ready: {result.get('name')}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при создании DOM Ready триггера: {str(e)}")
            raise

    def create_ga4_configuration_tag(self, measurement_id: str) -> Dict:
        """
        Создание тега конфигурации GA4.
        
        Args:
            measurement_id: Measurement ID из GA4
            
        Returns:
            Dict: Созданный тег
        """
        try:
            workspace_id = self.get_workspace_id()
            tag = {
                'name': 'GA4 Configuration',
                'type': 'gaawc',
                'parameter': [
                    {
                        'type': 'TEMPLATE',
                        'key': 'measurementId',
                        'value': measurement_id
                    },
                    {
                        'type': 'BOOLEAN',
                        'key': 'sendPageView',
                        'value': 'true'
                    }
                ],
                'firingTriggerId': [
                    self.create_page_view_trigger().get('triggerId')
                ]
            }
            
            result = self.service.accounts().containers().workspaces().tags().create(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=tag
            ).execute()
            
            logger.info(f"Создан тег GA4 Configuration: {result.get('name')}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при создании GA4 Configuration тега: {str(e)}")
            raise

    def create_add_to_cart_trigger(self) -> Dict:
        """
        Создание триггера для отслеживания добавления в корзину.
        
        Returns:
            Dict: Созданный триггер
        """
        try:
            workspace_id = self.get_workspace_id()
            trigger = {
                'name': 'Add to Cart Click',
                'type': 'domClick',
                'parameter': [
                    {
                        'type': 'BOOLEAN',
                        'key': 'waitForTags',
                        'value': 'false'
                    },
                    {
                        'type': 'BOOLEAN',
                        'key': 'checkValidation',
                        'value': 'false'
                    },
                    {
                        'type': 'TEMPLATE',
                        'key': 'clickElement',
                        'value': '.add-to-cart-button'
                    }
                ]
            }
            
            result = self.service.accounts().containers().workspaces().triggers().create(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=trigger
            ).execute()
            
            logger.info(f"Создан триггер Add to Cart: {result.get('name')}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при создании Add to Cart триггера: {str(e)}")
            raise

    def create_add_to_cart_tag(self, trigger_id: str) -> Dict:
        """
        Создание тега для отправки события добавления в корзину в GA4.
        
        Args:
            trigger_id: ID триггера для срабатывания
            
        Returns:
            Dict: Созданный тег
        """
        try:
            workspace_id = self.get_workspace_id()
            tag = {
                'name': 'GA4 - Add to Cart Event',
                'type': 'gaawe',
                'parameter': [
                    {
                        'type': 'TEMPLATE',
                        'key': 'eventName',
                        'value': 'add_to_cart'
                    },
                    {
                        'type': 'LIST',
                        'key': 'eventParameters',
                        'list': [
                            {
                                'type': 'MAP',
                                'map': [
                                    {
                                        'type': 'TEMPLATE',
                                        'key': 'name',
                                        'value': 'currency'
                                    },
                                    {
                                        'type': 'TEMPLATE',
                                        'key': 'value',
                                        'value': 'KZT'
                                    }
                                ]
                            },
                            {
                                'type': 'MAP',
                                'map': [
                                    {
                                        'type': 'TEMPLATE',
                                        'key': 'name',
                                        'value': 'items'
                                    },
                                    {
                                        'type': 'TEMPLATE',
                                        'key': 'value',
                                        'value': '{{Click Element}}'
                                    }
                                ]
                            }
                        ]
                    }
                ],
                'firingTriggerId': [trigger_id]
            }
            
            result = self.service.accounts().containers().workspaces().tags().create(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=tag
            ).execute()
            
            logger.info(f"Создан тег Add to Cart: {result.get('name')}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при создании Add to Cart тега: {str(e)}")
            raise

    def setup_basic_tracking(self, measurement_id: str) -> None:
        """
        Настройка базового отслеживания с GA4.
        
        Args:
            measurement_id: Measurement ID из GA4
        """
        try:
            workspace_id = self.get_workspace_id()
            
            # Создаем тег GA4 Configuration
            tag = {
                'name': 'GA4 Configuration',
                'type': 'gaawc',
                'parameter': [
                    {
                        'type': 'template',
                        'key': 'measurementId',
                        'value': measurement_id
                    }
                ]
            }
            
            result = self.service.accounts().containers().workspaces().tags().create(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=tag
            ).execute()
            
            logger.info(f"Создан тег GA4 Configuration: {result.get('name')}")
            
            # Создаем триггер All Pages
            trigger = {
                'name': 'All Pages',
                'type': 'pageview'
            }
            
            trigger_result = self.service.accounts().containers().workspaces().triggers().create(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=trigger
            ).execute()
            
            logger.info(f"Создан триггер: {trigger_result.get('name')}")
            
            # Связываем тег с триггером
            tag_update = {
                'name': result['name'],
                'type': 'gaawc',
                'parameter': result['parameter'],
                'firingTriggerId': [trigger_result['triggerId']]
            }
            
            updated_result = self.service.accounts().containers().workspaces().tags().update(
                path=result['path'],
                body=tag_update
            ).execute()
            
            logger.info(f"Тег обновлен и связан с триггером: {updated_result.get('name')}")
            
            # Создаем тег GA4 Event
            event_tag = {
                'name': 'GA4 Event',
                'type': 'gaawe',
                'parameter': [
                    {
                        'type': 'template',
                        'key': 'eventName',
                        'value': 'page_view'
                    }
                ]
            }
            
            event_result = self.service.accounts().containers().workspaces().tags().create(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=event_tag
            ).execute()
            
            logger.info(f"Создан тег GA4 Event: {event_result.get('name')}")
            
            # Связываем тег события с триггером
            event_tag_update = {
                'name': event_result['name'],
                'type': 'gaawe',
                'parameter': event_result['parameter'],
                'firingTriggerId': [trigger_result['triggerId']]
            }
            
            updated_event_result = self.service.accounts().containers().workspaces().tags().update(
                path=event_result['path'],
                body=event_tag_update
            ).execute()
            
            logger.info(f"Тег события обновлен и связан с триггером: {updated_event_result.get('name')}")
            
        except Exception as e:
            logger.error(f"Ошибка при настройке базового отслеживания: {str(e)}")
            raise

    def create_test_tag(self) -> Dict:
        """
        Создание тестового HTML тега для проверки доступов.
        
        Returns:
            Dict: Созданный тег
        """
        try:
            workspace_id = self.get_workspace_id()
            tag = {
                'name': 'Test HTML Tag',
                'type': 'html',
                'parameter': [
                    {
                        'type': 'TEMPLATE',
                        'key': 'html',
                        'value': '<script>console.log("Test tag loaded");</script>'
                    }
                ]
            }
            
            result = self.service.accounts().containers().workspaces().tags().create(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=tag
            ).execute()
            
            logger.info(f"Создан тестовый тег: {result.get('name')}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при создании тестового тега: {str(e)}")
            raise

    def test_permissions(self):
        """
        Проверка доступов к GTM API
        """
        try:
            self.create_test_tag()
            logger.info("Доступы к GTM API работают корректно")
        except Exception as e:
            logger.error(f"Ошибка при проверке доступов к GTM API: {str(e)}")
            raise

    def check_permissions(self) -> None:
        """Проверка разрешений для работы с GTM API."""
        try:
            # Пробуем получить список тегов
            tags = self.service.accounts().containers().workspaces().tags().list(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/2'
            ).execute()
            
            logger.info(f"Успешно получен список тегов: {len(tags.get('tag', []))} тегов")
            
            # Пробуем получить список триггеров
            triggers = self.service.accounts().containers().workspaces().triggers().list(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/2'
            ).execute()
            
            logger.info(f"Успешно получен список триггеров: {len(triggers.get('trigger', []))} триггеров")
            
            # Пробуем получить список переменных
            variables = self.service.accounts().containers().workspaces().variables().list(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/2'
            ).execute()
            
            logger.info(f"Успешно получен список переменных: {len(variables.get('variable', []))} переменных")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при проверке разрешений: {str(e)}")
            raise

    def setup_ga4_tag(self, measurement_id: str) -> dict:
        """
        Создает тег GA4 Configuration в контейнере
        
        Args:
            measurement_id: ID измерения GA4 (например, G-XXXXXXXX)
            
        Returns:
            dict: Созданный тег
        """
        try:
            workspace_id = self.get_workspace_id()
            
            # Создаем тег GA4 Configuration
            tag_body = {
                'name': 'GA4 Configuration',
                'type': 'gaawc',
                'parameter': [
                    {
                        'type': 'template',
                        'key': 'measurementId',
                        'value': measurement_id
                    }
                ]
            }
            
            request = self.service.accounts().containers().workspaces().tags().create(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=tag_body
            )
            
            response = request.execute()
            logger.info(f"Создан тег GA4 Configuration: {response['name']}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка при создании тега GA4: {str(e)}")
            raise

    def setup_ga4_events(self, ga4_config_tag_id: str) -> list:
        """
        Создает основные теги событий GA4
        
        Args:
            ga4_config_tag_id: ID тега GA4 Configuration
            
        Returns:
            list: Список созданных тегов
        """
        try:
            workspace_id = self.get_workspace_id()
            created_tags = []
            
            # Получаем measurement_id из базы данных
            ga4_creds = self.db.get_credentials('ga4')
            if not ga4_creds:
                raise Exception("Не найдены учетные данные GA4")
            
            measurement_id = ga4_creds['credentials']['measurement_id']
            
            # Список событий для отслеживания
            events = [
                {
                    'name': 'GA4 - Click',
                    'trigger': 'Click - All Elements',
                    'event_name': 'click'
                },
                {
                    'name': 'GA4 - Page View',
                    'trigger': 'Page View - All Pages',
                    'event_name': 'page_view'
                },
                {
                    'name': 'GA4 - Scroll',
                    'trigger': 'Scroll Depth',
                    'event_name': 'scroll'
                }
            ]
            
            for event in events:
                # Задержка перед созданием триггера
                time.sleep(5)
                
                # Создаем триггер
                trigger = self.create_trigger(event['trigger'])
                
                # Задержка перед созданием тега
                time.sleep(5)
                
                # Создаем тег события
                tag_body = {
                    'name': event['name'],
                    'type': 'gaawe',
                    'parameter': [
                        {
                            'type': 'template',
                            'key': 'eventName',
                            'value': event['event_name']
                        },
                        {
                            'type': 'template',
                            'key': 'measurementIdOverride',
                            'value': measurement_id
                        }
                    ],
                    'firingTriggerId': [trigger['triggerId']],
                    'tagFiringOption': 'oncePerEvent'
                }
                
                request = self.service.accounts().containers().workspaces().tags().create(
                    parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                    body=tag_body
                )
                
                response = request.execute()
                created_tags.append(response)
                logger.info(f"Создан тег события {event['name']}: {response['name']}")
                
                # Задержка после создания тега
                time.sleep(5)
            
            return created_tags
            
        except Exception as e:
            logger.error(f"Ошибка при создании тегов событий GA4: {str(e)}")
            raise

    def create_trigger(self, trigger_type: str) -> dict:
        """
        Создает триггер указанного типа
        
        Args:
            trigger_type: Тип триггера
            
        Returns:
            dict: Созданный триггер
        """
        try:
            workspace_id = self.get_workspace_id()
            
            trigger_config = {
                'Click - All Elements': {
                    'type': 'CLICK',
                    'filter': []
                },
                'Page View - All Pages': {
                    'type': 'PAGEVIEW',
                    'filter': []
                },
                'Scroll Depth': {
                    'type': 'SCROLL_DEPTH',
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
            }
            
            config = trigger_config.get(trigger_type)
            if not config:
                raise ValueError(f"Неизвестный тип триггера: {trigger_type}")
                
            trigger_body = {
                'name': trigger_type,
                'type': config['type']
            }
            
            if 'filter' in config:
                trigger_body['filter'] = config['filter']
            if 'parameter' in config:
                trigger_body['parameter'] = config['parameter']
            
            request = self.service.accounts().containers().workspaces().triggers().create(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=trigger_body
            )
            
            response = request.execute()
            logger.info(f"Создан триггер {trigger_type}: {response['name']}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка при создании триггера: {str(e)}")
            raise

    def publish_workspace(self) -> dict:
        """
        Публикует текущую рабочую область
        
        Returns:
            dict: Результат публикации
        """
        try:
            workspace_id = self.get_workspace_id()
            
            # Создаем версию
            version_body = {
                'name': f'Version {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'notes': 'Автоматическое обновление через API'
            }
            
            create_version_request = self.service.accounts().containers().workspaces().create_version(
                path=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=version_body
            )
            
            version_response = create_version_request.execute()
            logger.info(f"Создана новая версия: {version_response.get('containerVersion', {}).get('name')}")
            
            # Публикуем версию
            version_number = version_response.get('containerVersion', {}).get('containerVersionId')
            if version_number:
                publish_request = self.service.accounts().containers().versions().publish(
                    path=f'accounts/{self.account_id}/containers/{self.container_id}/versions/{version_number}'
                )
                publish_response = publish_request.execute()
                logger.info(f"Версия опубликована: {publish_response.get('containerVersion', {}).get('name')}")
                return publish_response
            else:
                raise Exception("Не удалось получить номер версии")
            
        except Exception as e:
            logger.error(f"Ошибка при публикации рабочей области: {str(e)}")
            raise

    def check_container_access(self) -> dict:
        """
        Проверяет доступ к контейнеру и возвращает информацию о нем
        
        Returns:
            dict: Информация о контейнере
        """
        try:
            request = self.service.accounts().containers().get(
                path=f'accounts/{self.account_id}/containers/{self.container_id}'
            )
            response = request.execute()
            logger.info(f"Получена информация о контейнере: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка при проверке доступа к контейнеру: {str(e)}")
            raise

    def list_containers(self) -> List[Dict]:
        """
        Получает список всех контейнеров в аккаунте
        
        Returns:
            List[Dict]: Список контейнеров
        """
        try:
            request = self.service.accounts().containers().list(
                parent=f'accounts/{self.account_id}'
            )
            response = request.execute()
            containers = response.get('container', [])
            logger.info(f"Получен список контейнеров: {containers}")
            return containers
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка контейнеров: {str(e)}")
            raise

    def list_tags(self) -> List[Dict]:
        """
        Получает список всех тегов в рабочей области
        
        Returns:
            List[Dict]: Список тегов
        """
        try:
            workspace_id = self.get_workspace_id()
            
            request = self.service.accounts().containers().workspaces().tags().list(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}'
            )
            response = request.execute()
            tags = response.get('tag', [])
            logger.info(f"Получен список тегов: {tags}")
            return tags
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка тегов: {str(e)}")
            raise
            
    def delete_tag(self, tag_path: str):
        """
        Удаляет тег по его пути
        
        Args:
            tag_path: Путь к тегу
        """
        try:
            request = self.service.accounts().containers().workspaces().tags().delete(
                path=tag_path
            )
            request.execute()
            logger.info(f"Тег удален: {tag_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при удалении тега: {str(e)}")
            raise
            
    def delete_all_tags(self):
        """
        Удаляет все теги в рабочей области
        """
        try:
            tags = self.list_tags()
            for tag in tags:
                self.delete_tag(tag['path'])
                time.sleep(5)  # Задержка 5 секунд между запросами
            logger.info("Все теги удалены")
            time.sleep(5)  # Дополнительная задержка после удаления всех тегов
            
        except Exception as e:
            logger.error(f"Ошибка при удалении тегов: {str(e)}")
            raise

    def list_triggers(self) -> List[Dict]:
        """
        Получает список всех триггеров в рабочей области
        
        Returns:
            List[Dict]: Список триггеров
        """
        try:
            workspace_id = self.get_workspace_id()
            
            request = self.service.accounts().containers().workspaces().triggers().list(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}'
            )
            response = request.execute()
            triggers = response.get('trigger', [])
            logger.info(f"Получен список триггеров: {triggers}")
            return triggers
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка триггеров: {str(e)}")
            raise
            
    def delete_trigger(self, trigger_path: str):
        """
        Удаляет триггер по его пути
        
        Args:
            trigger_path: Путь к триггеру
        """
        try:
            request = self.service.accounts().containers().workspaces().triggers().delete(
                path=trigger_path
            )
            request.execute()
            logger.info(f"Триггер удален: {trigger_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при удалении триггера: {str(e)}")
            raise
            
    def delete_all_triggers(self):
        """
        Удаляет все триггеры в рабочей области
        """
        try:
            triggers = self.list_triggers()
            for trigger in triggers:
                self.delete_trigger(trigger['path'])
                time.sleep(5)  # Задержка 5 секунд между запросами
            logger.info("Все триггеры удалены")
            time.sleep(5)  # Дополнительная задержка после удаления всех триггеров
            
        except Exception as e:
            logger.error(f"Ошибка при удалении триггеров: {str(e)}")
            raise

    def create_ecommerce_trigger(self, trigger_type: str, event_name: str) -> dict:
        """
        Создает триггер для отслеживания e-commerce событий
        
        Args:
            trigger_type: Тип триггера (Custom Event)
            event_name: Название события (view_item, add_to_cart и т.д.)
            
        Returns:
            dict: Созданный триггер
        """
        try:
            workspace_id = self.get_workspace_id()
            
            trigger_body = {
                'name': f'Event - {event_name}',
                'type': 'customEvent',
                'customEventFilter': [
                    {
                        'type': 'equals',
                        'parameter': [
                            {
                                'type': 'template',
                                'key': 'event',
                                'value': event_name
                            }
                        ]
                    }
                ]
            }
            
            request = self.service.accounts().containers().workspaces().triggers().create(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=trigger_body
            )
            
            response = request.execute()
            logger.info(f"Создан триггер для события {event_name}: {response['name']}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка при создании триггера для события {event_name}: {str(e)}")
            raise
            
    def setup_ecommerce_triggers(self) -> dict:
        """
        Создает все необходимые триггеры для e-commerce
        
        Returns:
            dict: Словарь с ID созданных триггеров
        """
        try:
            # Список e-commerce событий
            events = [
                'view_item',
                'add_to_cart',
                'begin_checkout',
                'purchase',
                'refund',
                'view_item_list'
            ]
            
            triggers = {}
            for event in events:
                time.sleep(2)  # Задержка между запросами
                trigger = self.create_ecommerce_trigger('customEvent', event)
                triggers[event] = trigger['triggerId']
                
            logger.info("Созданы все триггеры для e-commerce")
            return triggers
            
        except Exception as e:
            logger.error(f"Ошибка при создании триггеров для e-commerce: {str(e)}")
            raise

    def create_ecommerce_tag(self, event_name: str, trigger_id: str, measurement_id: str) -> dict:
        """
        Создает тег для отслеживания e-commerce события
        
        Args:
            event_name: Название события (view_item, add_to_cart и т.д.)
            trigger_id: ID триггера для срабатывания
            measurement_id: Measurement ID из GA4
            
        Returns:
            dict: Созданный тег
        """
        try:
            workspace_id = self.get_workspace_id()
            
            # Базовые параметры для всех событий
            parameters = [
                {
                    'type': 'template',
                    'key': 'eventName',
                    'value': event_name
                },
                {
                    'type': 'template',
                    'key': 'measurementIdOverride',
                    'value': measurement_id
                }
            ]
            
            # Добавляем параметры в зависимости от типа события
            if event_name in ['view_item', 'add_to_cart', 'purchase', 'refund']:
                parameters.extend([
                    {
                        'type': 'template',
                        'key': 'items',
                        'value': '{{ecommerce.items}}'
                    }
                ])
                
            if event_name in ['purchase', 'refund']:
                parameters.extend([
                    {
                        'type': 'template',
                        'key': 'transaction_id',
                        'value': '{{ecommerce.transaction_id}}'
                    },
                    {
                        'type': 'template',
                        'key': 'value',
                        'value': '{{ecommerce.value}}'
                    },
                    {
                        'type': 'template',
                        'key': 'currency',
                        'value': '{{ecommerce.currency}}'
                    }
                ])
            
            tag_body = {
                'name': f'GA4 - {event_name}',
                'type': 'gaawe',  # Google Analytics: GA4 Event
                'parameter': parameters,
                'firingTriggerId': [trigger_id],
                'tagFiringOption': 'oncePerEvent'
            }
            
            request = self.service.accounts().containers().workspaces().tags().create(
                parent=f'accounts/{self.account_id}/containers/{self.container_id}/workspaces/{workspace_id}',
                body=tag_body
            )
            
            response = request.execute()
            logger.info(f"Создан тег для события {event_name}: {response['name']}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка при создании тега для события {event_name}: {str(e)}")
            raise
            
    def setup_ecommerce_tags(self, triggers: dict) -> list:
        """
        Создает все необходимые теги для e-commerce
        
        Args:
            triggers: Словарь с ID триггеров
            
        Returns:
            list: Список созданных тегов
        """
        try:
            # Получаем measurement_id из базы данных
            ga4_creds = self.db.get_credentials('ga4')
            if not ga4_creds:
                raise Exception("Не найдены учетные данные GA4")
            
            measurement_id = ga4_creds['credentials']['measurement_id']
            
            tags = []
            for event_name, trigger_id in triggers.items():
                time.sleep(2)  # Задержка между запросами
                tag = self.create_ecommerce_tag(event_name, trigger_id, measurement_id)
                tags.append(tag)
                
            logger.info("Созданы все теги для e-commerce")
            return tags
            
        except Exception as e:
            logger.error(f"Ошибка при создании тегов для e-commerce: {str(e)}")
            raise

    def setup_ecommerce(self) -> dict:
        """
        Настраивает отслеживание электронной коммерции в GTM
        
        Returns:
            dict: Результат настройки
        """
        try:
            # Создаем триггеры
            triggers = self.setup_ecommerce_triggers()
            logger.info("Триггеры e-commerce настроены")
            
            # Создаем теги
            tags = self.setup_ecommerce_tags(triggers)
            logger.info("Теги e-commerce настроены")
            
            # Публикуем изменения
            version = self.publish_workspace()
            logger.info("Изменения опубликованы")
            
            return {
                'triggers': triggers,
                'tags': tags,
                'version': version
            }
            
        except Exception as e:
            logger.error(f"Ошибка при настройке e-commerce: {str(e)}")
            raise
