"""Скрипт для отправки отчета в Telegram."""
import os
import sys
from datetime import datetime
import psycopg2

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.config.supabase_config import DATABASE_URL
from src.services.telegram_service import TelegramService
from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def format_number(num):
    """Форматирует число с разделителями."""
    return f"{num:,}".replace(',', ' ')

def get_report_data(date):
    """Получает данные для отчета."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    data = {
        'query_types': [],
        'cities': [],
        'top_queries': []
    }
    
    try:
        # Статистика по типам запросов
        cur.execute("""
            SELECT query_type, COUNT(*) as count, SUM(clicks) as clicks, SUM(impressions) as impressions
            FROM search_queries_daily
            WHERE date = %s
            GROUP BY query_type
            ORDER BY clicks DESC
        """, (date,))
        data['query_types'] = cur.fetchall()
        
        # Статистика по городам
        cur.execute("""
            SELECT city, COUNT(*) as count, SUM(clicks) as clicks, SUM(impressions) as impressions
            FROM search_queries_daily
            WHERE date = %s
            GROUP BY city
            ORDER BY clicks DESC
        """, (date,))
        data['cities'] = cur.fetchall()
        
        # Топ-10 запросов
        cur.execute("""
            SELECT query, query_type, city, clicks, impressions, position
            FROM search_queries_daily
            WHERE date = %s
            ORDER BY clicks DESC
            LIMIT 10
        """, (date,))
        data['top_queries'] = cur.fetchall()
        
    except Exception as e:
        logger.error(f"Ошибка при получении данных: {e}")
    finally:
        cur.close()
        conn.close()
        
    return data

def format_report(date, data):
    """Форматирует отчет."""
    message = f"📊 Отчет по SEO за {date.strftime('%d.%m.%Y')}\n\n"
    
    # Общая статистика
    total_clicks = sum(row[2] for row in data['query_types'])
    total_impressions = sum(row[3] for row in data['query_types'])
    total_queries = sum(row[1] for row in data['query_types'])
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    message += (
        f"🌐 ОБЩАЯ СТАТИСТИКА:\n"
        f"👆 Клики: {format_number(total_clicks)}\n"
        f"👀 Показы: {format_number(total_impressions)}\n"
        f"🔍 Запросов: {format_number(total_queries)}\n"
        f"CTR: {ctr:.2f}%\n\n"
    )
    
    # Статистика по типам запросов
    message += "📝 ПО ТИПАМ ЗАПРОСОВ:\n"
    for row in data['query_types']:
        query_type, count, clicks, impressions = row
        query_ctr = (clicks / impressions * 100) if impressions > 0 else 0
        message += (
            f"\n{query_type.upper()}:\n"
            f"👆 Клики: {format_number(clicks)}\n"
            f"👀 Показы: {format_number(impressions)}\n"
            f"🔍 Запросов: {format_number(count)}\n"
            f"CTR: {query_ctr:.2f}%\n"
        )
    
    message += "\n"
    
    # Статистика по городам
    message += "🏙 ПО ГОРОДАМ:\n"
    for row in data['cities']:
        city, count, clicks, impressions = row
        city_ctr = (clicks / impressions * 100) if impressions > 0 else 0
        message += (
            f"\n{city.upper()}:\n"
            f"👆 Клики: {format_number(clicks)}\n"
            f"👀 Показы: {format_number(impressions)}\n"
            f"🔍 Запросов: {format_number(count)}\n"
            f"CTR: {city_ctr:.2f}%\n"
        )
    
    message += "\n"
    
    # Топ-10 запросов
    message += "🔝 ТОП-10 ЗАПРОСОВ:\n"
    for i, row in enumerate(data['top_queries'], 1):
        query, query_type, city, clicks, impressions, position = row
        query_ctr = (clicks / impressions * 100) if impressions > 0 else 0
        message += (
            f"\n{i}. {query}\n"
            f"👆 Клики: {clicks}\n"
            f"👀 Показы: {impressions}\n"
            f"CTR: {query_ctr:.2f}%\n"
            f"Позиция: {position:.1f}\n"
            f"Тип: {query_type}\n"
            f"Город: {city}\n"
        )
    
    return message

def main():
    """Main function."""
    try:
        logger.info("Начинаем отправку отчета...")
        
        # Инициализируем сервисы
        telegram = TelegramService()
        creds = CredentialsManager()
        
        # Получаем chat_id из базы
        chat_id = creds.get_credential('telegram', 'channel_id')
        
        # Получаем данные за 11 декабря 2023
        target_date = datetime(2023, 12, 11).date()
        logger.info(f"Формируем отчет за {target_date}")
        
        # Получаем данные
        data = get_report_data(target_date)
        
        # Форматируем отчет
        message = format_report(target_date, data)
        
        # Отправляем отчет
        telegram.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML'
        )
        
        logger.info(f"Отчет за {target_date} успешно отправлен!")
        
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
