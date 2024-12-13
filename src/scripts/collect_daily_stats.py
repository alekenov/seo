"""Скрипт для сбора ежедневной статистики."""
import os
import sys
import re
from datetime import datetime, timedelta
from typing import List, Dict

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.config.supabase_config import DATABASE_URL
from src.services.gsc_service import GSCService
from src.services.telegram_service import TelegramService
from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_city_from_page(page: str) -> str:
    """Получаем город из URL страницы."""
    # Убираем протокол и домен
    page = page.replace('https://cvety.kz/', '').replace('https://blog.cvety.kz/', 'blog/')
    
    # Маппинг городов
    city_mapping = {
        'almaty': 'алматы',
        'astana': 'астана',
        'shymkent': 'шымкент'
    }
    
    # Проверяем блог
    if page.startswith('blog/'):
        return 'блог'
        
    # Проверяем города
    for eng, rus in city_mapping.items():
        if page.startswith(f"{eng}/"):
            return rus
            
    return 'общий'

def get_query_type(query: str) -> str:
    """Определяем тип запроса."""
    query = query.lower()
    
    # Брендовые запросы
    if any(brand in query for brand in ['cvety.kz', 'цветы.кз', 'цветы кз']):
        return 'брендовый'
        
    # Коммерческие запросы
    if any(word in query for word in ['купить', 'заказать', 'цена', 'стоимость', 'сколько стоит']):
        return 'коммерческий'
        
    # Запросы по доставке
    if 'доставка' in query:
        return 'доставка'
        
    # Информационные запросы
    if any(word in query for word in ['как', 'что', 'когда', 'где', 'почему']):
        return 'информационный'
        
    # Запросы по типам цветов
    if any(flower in query for flower in ['розы', 'тюльпаны', 'пионы', 'хризантемы']):
        return 'типы_цветов'
        
    # По умолчанию - прочие
    return 'прочее'

def filter_and_sort_rows(rows: List[Dict]) -> List[Dict]:
    """Фильтруем и сортируем строки."""
    # Сортируем по кликам
    rows.sort(key=lambda x: x['clicks'], reverse=True)
    
    # Берем только первые 50
    return rows[:50]

def save_daily_stats(stats, date):
    """Сохраняем статистику в БД."""
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    total_clicks = 0
    total_impressions = 0
    total_queries = 0
    
    # Словарь для хранения статистики по городам
    city_stats = {}
    
    # Словарь для хранения статистики по типам запросов
    query_type_stats = {}
    
    # Фильтруем и сортируем строки
    rows = filter_and_sort_rows(stats.get('rows', []))
    
    for row in rows:
        # Получаем данные из строки
        dimensions = row['keys']
        page, query = dimensions[0], dimensions[1]
        
        # Получаем город и тип запроса
        city = get_city_from_page(page)
        query_type = get_query_type(query)
        
        # Получаем метрики
        clicks = row['clicks']
        impressions = row['impressions']
        position = row['position']
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        
        # Суммируем для общего отчета
        total_clicks += clicks
        total_impressions += impressions
        total_queries += 1
        
        # Суммируем для отчета по городам
        if city not in city_stats:
            city_stats[city] = {
                'clicks': 0,
                'impressions': 0,
                'queries': 0
            }
        city_stats[city]['clicks'] += clicks
        city_stats[city]['impressions'] += impressions
        city_stats[city]['queries'] += 1
        
        # Суммируем для отчета по типам запросов
        if query_type not in query_type_stats:
            query_type_stats[query_type] = {
                'clicks': 0,
                'impressions': 0,
                'queries': 0
            }
        query_type_stats[query_type]['clicks'] += clicks
        query_type_stats[query_type]['impressions'] += impressions
        query_type_stats[query_type]['queries'] += 1
        
        try:
            cur.execute("""
                INSERT INTO search_queries_daily 
                    (date, query, query_type, clicks, impressions, position, ctr, city)
                VALUES 
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, query, city) DO UPDATE SET
                    query_type = EXCLUDED.query_type,
                    clicks = EXCLUDED.clicks,
                    impressions = EXCLUDED.impressions,
                    position = EXCLUDED.position,
                    ctr = EXCLUDED.ctr
            """, (
                date,
                query,
                query_type,
                clicks,
                impressions,
                position,
                ctr,
                city
            ))
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных для запроса {query}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    return total_clicks, total_impressions, total_queries, city_stats, query_type_stats

def main():
    """Main function."""
    try:
        logger.info("Начинаем сбор ежедневной статистики...")
        
        # Инициализируем сервисы
        gsc = GSCService()
        telegram = TelegramService()
        creds = CredentialsManager()
        
        # Получаем chat_id из базы
        chat_id = creds.get_credential('telegram', 'channel_id')
        
        # Получаем данные за позавчера (GSC обновляет данные с задержкой)
        target_date = datetime.now().date() - timedelta(days=2)
        logger.info(f"Собираем данные за {target_date}")
        
        # Получаем статистику
        response = gsc.get_search_analytics(
            start_date=target_date,
            end_date=target_date,
            dimensions=['page', 'query', 'date']
        )
        
        # Сохраняем статистику в базу
        if response and 'rows' in response:
            # Сохраняем в базу и получаем суммарные показатели
            total_clicks, total_impressions, total_queries, city_stats, query_type_stats = save_daily_stats(response, target_date)
            
            # Формируем сообщение
            message = f"📊 ТОП-50 запросов за {target_date.strftime('%Y-%m-%d')}\n\n"
            
            # Общая статистика
            message += (
                f"🌐 ОБЩАЯ СТАТИСТИКА:\n"
                f"👆 Клики: {total_clicks}\n"
                f"👀 Показы: {total_impressions:,}\n"
                f"🔍 Запросов: {total_queries}\n"
                f"CTR: {(total_clicks / total_impressions * 100):.2f}%\n\n"
            )
            
            # Статистика по типам запросов
            message += "📝 ПО ТИПАМ ЗАПРОСОВ:\n"
            for query_type, stats in query_type_stats.items():
                query_ctr = (stats['clicks'] / stats['impressions'] * 100) if stats['impressions'] > 0 else 0
                message += (
                    f"\n{query_type.upper()}:\n"
                    f"👆 Клики: {stats['clicks']}\n"
                    f"👀 Показы: {stats['impressions']:,}\n"
                    f"🔍 Запросов: {stats['queries']}\n"
                    f"CTR: {query_ctr:.2f}%\n"
                )
            
            message += "\n"
            
            # Статистика по городам
            message += "🏙 ПО ГОРОДАМ:\n"
            for city, stats in city_stats.items():
                city_ctr = (stats['clicks'] / stats['impressions'] * 100) if stats['impressions'] > 0 else 0
                message += (
                    f"\n{city.upper()}:\n"
                    f"👆 Клики: {stats['clicks']}\n"
                    f"👀 Показы: {stats['impressions']:,}\n"
                    f"🔍 Запросов: {stats['queries']}\n"
                    f"CTR: {city_ctr:.2f}%\n"
                )
            
            # Отправляем уведомление
            telegram.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"Статистика за {target_date.strftime('%Y-%m-%d')} успешно сохранена!")
            
        else:
            error_msg = "❌ Нет данных в ответе от GSC API"
            logger.error(error_msg)
            telegram.send_message(chat_id=chat_id, text=error_msg)
            
    except Exception as e:
        error_msg = f"❌ Ошибка: {str(e)}"
        logger.error(error_msg)
        
        # Отправляем уведомление об ошибке
        try:
            telegram.send_message(chat_id=chat_id, text=error_msg)
        except:
            logger.error("Не удалось отправить уведомление об ошибке в Telegram")

if __name__ == "__main__":
    main()
