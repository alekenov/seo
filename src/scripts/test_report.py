"""Скрипт для тестирования отправки отчета."""

import psycopg2
from datetime import datetime, timedelta
from src.config.supabase_config import DATABASE_URL
from src.services.telegram_service import TelegramService
from src.utils.credentials_manager import CredentialsManager

def get_db_connection():
    """Получаем подключение к базе данных."""
    return psycopg2.connect(DATABASE_URL)

def format_metrics(metrics):
    """Форматируем метрики для отправки в Telegram."""
    report = "📊 *Еженедельный отчет по SEO*\n\n"
    
    # Общая статистика
    report += "*Общие метрики по типам запросов:*\n\n"
    for metric in metrics['general']:
        # Пропускаем брендовые запросы
        if metric['query_type'] == 'брендовый':
            continue
            
        report += f"*{metric['query_type']}*\n"
        report += f"📈 Всего запросов: {metric['total_queries']}\n"
        report += f"👆 Клики: {metric['clicks']}\n"
        report += f"👀 Показы: {metric['impressions']}\n"
        report += f"📍 Средняя позиция: {metric['avg_position']:.1f}\n"
        report += f"📊 Средний CTR: {metric['avg_ctr']:.2f}%\n\n"
    
    # Топ запросов
    report += "*Топ 10 небрендовых поисковых запросов:*\n\n"
    query_count = 0
    for query in metrics['top_queries']:
        # Пропускаем брендовые запросы (cvety kz, цветы кз и т.д.)
        query_lower = query['query'].lower()
        if 'cvety' in query_lower or 'цветы кз' in query_lower:
            continue
            
        query_count += 1
        report += f"{query_count}. *{query['query']}*\n"
        report += f"👆 Клики: {query['clicks']}\n"
        report += f"👀 Показы: {query['impressions']}\n"
        report += f"📍 Позиция: {query['position']:.1f}\n"
        report += f"📊 CTR: {query['ctr']:.2f}%\n\n"
        
        if query_count >= 10:
            break
    
    return report

def get_metrics():
    """Получаем метрики из базы данных."""
    print("Получаем метрики из базы данных...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Получаем общие метрики по типам запросов
    cur.execute("""
        SELECT 
            query_type,
            COUNT(*) as total_queries,
            SUM(clicks) as clicks,
            SUM(impressions) as impressions,
            AVG(position) as avg_position,
            (SUM(clicks)::float / SUM(impressions) * 100) as avg_ctr
        FROM search_queries
        GROUP BY query_type
    """)
    general_metrics = []
    for row in cur.fetchall():
        general_metrics.append({
            'query_type': row[0],
            'total_queries': row[1],
            'clicks': row[2],
            'impressions': row[3],
            'avg_position': row[4],
            'avg_ctr': row[5]
        })
    
    # Получаем топ запросов (исключая брендовые)
    cur.execute("""
        SELECT 
            query,
            SUM(clicks) as clicks,
            SUM(impressions) as impressions,
            AVG(position) as position,
            (SUM(clicks)::float / SUM(impressions) * 100) as ctr
        FROM search_queries
        WHERE query_type != 'брендовый'
        GROUP BY query
        ORDER BY SUM(clicks) DESC
        LIMIT 20
    """)
    top_queries = []
    for row in cur.fetchall():
        top_queries.append({
            'query': row[0],
            'clicks': row[1],
            'impressions': row[2],
            'position': row[3],
            'ctr': row[4]
        })
    
    cur.close()
    conn.close()
    
    return {
        'general': general_metrics,
        'top_queries': top_queries
    }

def main():
    """Основная функция."""
    try:
        # Получаем метрики
        metrics = get_metrics()
        
        # Форматируем отчет
        report_text = format_metrics(metrics)
        
        # Отправляем в Telegram
        creds = CredentialsManager().load_credentials('telegram')
        telegram = TelegramService(creds['bot_token'])
        telegram.send_message(creds['channel_id'], report_text, parse_mode='Markdown')
        print("Отчет успешно отправлен в Telegram!")
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")

if __name__ == "__main__":
    main()
