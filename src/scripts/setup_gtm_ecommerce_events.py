"""
Скрипт для обновления e-commerce событий в GTM
"""

import logging
from src.services.gtm_service import GTMService
from src.database.db import SupabaseDB

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_custom_html_tag(gtm: GTMService, name: str, html_code: str):
    """Обновляет существующий Custom HTML тег"""
    try:
        workspace_id = gtm.get_workspace_id()
        
        # Получаем список тегов
        tags = gtm.service.accounts().containers().workspaces().tags().list(
            parent=f'accounts/{gtm.account_id}/containers/{gtm.container_id}/workspaces/{workspace_id}'
        ).execute().get('tag', [])
        
        # Ищем нужный тег
        target_tag = None
        for tag in tags:
            if tag['name'] == name:
                target_tag = tag
                break
                
        if not target_tag:
            logger.error(f"Тег {name} не найден")
            return None
            
        # Обновляем HTML код
        target_tag['parameter'] = [
            {
                'type': 'template',
                'key': 'html',
                'value': html_code
            }
        ]
        
        # Обновляем тег
        result = gtm.service.accounts().containers().workspaces().tags().update(
            path=target_tag['path'],
            body=target_tag
        ).execute()
        
        logger.info(f"Обновлен тег: {result['name']}")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении тега {name}: {str(e)}")
        raise

def main():
    """Основная функция"""
    try:
        # Инициализируем сервис GTM
        gtm = GTMService(SupabaseDB())
        
        # HTML код для отслеживания событий
        html_code = """
<script>
// Функция для отправки события в GA4
function sendGa4Event(eventName, eventParams) {
    gtag('event', eventName, eventParams);
}

// Слушатель для события view_item
document.addEventListener('view_item', function(e) {
    sendGa4Event('view_item', {
        item_id: e.detail.item_id,
        item_name: e.detail.item_name,
        price: e.detail.price
    });
});

// Слушатель для события add_to_cart
document.addEventListener('add_to_cart', function(e) {
    sendGa4Event('add_to_cart', {
        item_id: e.detail.item_id,
        item_name: e.detail.item_name,
        price: e.detail.price,
        quantity: e.detail.quantity
    });
});

// Слушатель для события begin_checkout
document.addEventListener('begin_checkout', function(e) {
    sendGa4Event('begin_checkout', {
        item_id: e.detail.item_id,
        item_name: e.detail.item_name,
        price: e.detail.price,
        quantity: e.detail.quantity,
        currency: e.detail.currency
    });
});

// Слушатель для события purchase
document.addEventListener('purchase', function(e) {
    sendGa4Event('purchase', {
        item_id: e.detail.item_id,
        item_name: e.detail.item_name,
        price: e.detail.price,
        quantity: e.detail.quantity,
        currency: e.detail.currency,
        transaction_id: e.detail.transaction_id
    });
});

// Слушатель для события refund
document.addEventListener('refund', function(e) {
    sendGa4Event('refund', {
        item_id: e.detail.item_id,
        item_name: e.detail.item_name,
        price: e.detail.price,
        quantity: e.detail.quantity,
        currency: e.detail.currency,
        transaction_id: e.detail.transaction_id
    });
});
</script>
"""
        
        # Обновляем тег
        update_custom_html_tag(gtm, 'E-commerce Event Listener', html_code)
        
        # Публикуем изменения
        gtm.publish_workspace()
        
        logger.info("E-commerce отслеживание успешно обновлено")
        
        # Выводим инструкции по использованию
        print("""
Для отправки событий используйте следующий код:

// Просмотр товара
document.dispatchEvent(new CustomEvent('view_item', {
    detail: {
        item_id: '12345',
        item_name: 'Product Name',
        price: 99.99
    }
}));

// Добавление в корзину
document.dispatchEvent(new CustomEvent('add_to_cart', {
    detail: {
        item_id: '12345',
        item_name: 'Product Name',
        price: 99.99,
        quantity: 1
    }
}));

// Начало оформления заказа
document.dispatchEvent(new CustomEvent('begin_checkout', {
    detail: {
        item_id: '12345',
        item_name: 'Product Name',
        price: 99.99,
        quantity: 1,
        currency: 'USD'
    }
}));

// Покупка
document.dispatchEvent(new CustomEvent('purchase', {
    detail: {
        item_id: '12345',
        item_name: 'Product Name',
        price: 99.99,
        quantity: 1,
        currency: 'USD',
        transaction_id: 'T12345'
    }
}));

// Возврат
document.dispatchEvent(new CustomEvent('refund', {
    detail: {
        item_id: '12345',
        item_name: 'Product Name',
        price: 99.99,
        quantity: 1,
        currency: 'USD',
        transaction_id: 'T12345'
    }
}));
""")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке e-commerce отслеживания: {str(e)}")
        raise

if __name__ == '__main__':
    main()
