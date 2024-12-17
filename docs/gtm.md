# Google Tag Manager Интеграция

## Текущее состояние

### 1. Базовая настройка GA4
- ✅ Установлен тег конфигурации GA4 (ID: G-X0F3KBN3ZT)
- ✅ Настроена отправка базовых событий:
  - Page View (просмотр страницы)
  - Click (клики по элементам)
  - Scroll (прокрутка страницы)

### 2. Теги
Всего тегов: 4
1. GA4 Configuration
   - Тип: googtag
   - ID измерения: G-X0F3KBN3ZT
   - Отправка просмотра страницы: включена

2. GA4 - Click
   - Тип: gaawe
   - Событие: click
   - Триггер: Click - All Elements (ID: 56)

3. GA4 - Page View
   - Тип: gaawe
   - Событие: page_view
   - Триггер: Page View - All Pages (ID: 58)

4. GA4 - Scroll
   - Тип: gaawe
   - Событие: scroll
   - Триггер: Scroll Depth (ID: 60)

### 3. Триггеры
Всего триггеров: 3
1. Click - All Elements
   - Тип: click
   - Отслеживает: все клики по элементам

2. Page View - All Pages
   - Тип: pageview
   - Отслеживает: загрузку страниц

3. Scroll Depth
   - Тип: scrollDepth
   - Отслеживает: глубину прокрутки

### 4. Переменные
Всего переменных: 1
- ✅ Настроены переменные DataLayer для e-commerce данных:
  - item_id
  - item_name
  - price
  - quantity
  - currency
  - transaction_id

## Необходимые доработки

### 1. Проверка и настройка прав доступа
- [ ] Проверить права сервисного аккаунта в GTM
- [ ] Убедиться в наличии всех необходимых разрешений:
  - https://www.googleapis.com/auth/tagmanager.edit.containers
  - https://www.googleapis.com/auth/tagmanager.publish
  - https://www.googleapis.com/auth/tagmanager.manage.accounts
  - https://www.googleapis.com/auth/tagmanager.delete.containers
  - https://www.googleapis.com/auth/tagmanager.edit.containerversions

### 2. Настройка E-commerce отслеживания
✅ Настроены переменные DataLayer для e-commerce данных:
  - item_id
  - item_name
  - price
  - quantity
  - currency
  - transaction_id

✅ Настроены события e-commerce:
1. view_item (просмотр товара)
   ```javascript
   document.dispatchEvent(new CustomEvent('view_item', {
       detail: {
           item_id: '12345',
           item_name: 'Product Name',
           price: 99.99
       }
   }));
   ```

2. add_to_cart (добавление в корзину)
   ```javascript
   document.dispatchEvent(new CustomEvent('add_to_cart', {
       detail: {
           item_id: '12345',
           item_name: 'Product Name',
           price: 99.99,
           quantity: 1
       }
   }));
   ```

3. begin_checkout (начало оформления)
   ```javascript
   document.dispatchEvent(new CustomEvent('begin_checkout', {
       detail: {
           item_id: '12345',
           item_name: 'Product Name',
           price: 99.99,
           quantity: 1,
           currency: 'USD'
       }
   }));
   ```

4. purchase (покупка)
   ```javascript
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
   ```

5. refund (возврат)
   ```javascript
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
   ```

✅ Настроен Custom HTML тег для прослушивания и отправки всех e-commerce событий в GA4

### 3. Тестирование и отладка
- [ ] Настроить режим предварительного просмотра в GTM
- [ ] Проверить корректность отправки всех событий
- [ ] Проверить корректность передачи данных в GA4

### 4. Документация и мониторинг
- [ ] Создать документацию по структуре данных e-commerce
- [ ] Настроить оповещения о проблемах с отправкой данных
- [ ] Создать дашборд для мониторинга e-commerce событий

## Инструкции для разработчиков

### 1. Установка GTM на сайт
- Добавить основной скрипт GTM в секцию `<head>`
- Добавить noscript-тег сразу после открывающего тега `<body>`
- ID контейнера GTM: GTM-202291559

### 2. Отправка e-commerce событий
Для корректной работы отслеживания e-commerce, необходимо вызывать события в следующие моменты:

1. view_item
   - Когда: при загрузке страницы товара
   - Обязательные параметры: item_id, item_name, price

2. add_to_cart
   - Когда: при клике на кнопку "В корзину"
   - Обязательные параметры: item_id, item_name, price, quantity

3. begin_checkout
   - Когда: при переходе к оформлению заказа
   - Обязательные параметры: item_id, item_name, price, quantity, currency

4. purchase
   - Когда: после успешной оплаты заказа
   - Обязательные параметры: item_id, item_name, price, quantity, currency, transaction_id

5. refund
   - Когда: при оформлении возврата
   - Обязательные параметры: item_id, item_name, price, quantity, currency, transaction_id

### 3. Проверка корректности отправки
1. Включить режим предварительного просмотра в GTM
2. Проверить отправку каждого события через консоль разработчика
3. Убедиться, что все параметры передаются корректно

## Известные проблемы
1. Ошибки при создании триггеров через API:
   - HTTP 400: Invalid value at 'trigger.filter[0].type'
   - HTTP 500: Internal Server Error

## Следующие шаги
1. Исправить проблемы с правами доступа сервисного аккаунта
2. Создать базовые переменные DataLayer
3. Настроить триггеры для e-commerce через UI GTM
4. Интегрировать созданные триггеры в API-скрипты
