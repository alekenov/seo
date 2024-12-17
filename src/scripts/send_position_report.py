"""Скрипт для отправки отчета по позициям в Telegram."""

from datetime import datetime, timedelta
from src.analytics.position_analyzer import EnhancedPositionAnalyzer
from src.services.telegram_service import TelegramService
from src.utils.credentials_manager import CredentialsManager
from src.database.postgres_client import PostgresClient
from typing import NamedTuple

class PositionChange(NamedTuple):
    query: str
    page_url: str
    city: str
    old_position: float
    new_position: float
    impressions_change: int
    clicks_change: int
    change: float

def format_position_changes(changes: list) -> str:
    """Форматирование изменений позиций для отчета."""
    if not changes:
        return "Значимых изменений позиций не обнаружено"
    
    report = "🎯 *Значимые изменения позиций:*\n\n"
    
    for change in changes:
        # Определяем эмодзи для изменения
        if change.new_position < change.old_position:
            emoji = "📈"  # Улучшение
        else:
            emoji = "📉"  # Ухудшение
            
        # Форматируем строку изменения
        report += (
            f"{emoji} `{change.query}`\n"
            f"    Позиция: {change.old_position:.1f} → {change.new_position:.1f} "
            f"({abs(change.change):.1f})\n"
            f"    Показы: {change.impressions_change:+d}\n"
            f"    Клики: {change.clicks_change:+d}\n"
            f"    Город: {change.city}\n"
            f"    URL: {change.page_url}\n\n"
        )
    
    return report


def main():
    """Основная функция для отправки отчета."""
    # Инициализируем сервисы
    db_client = PostgresClient()
    analyzer = EnhancedPositionAnalyzer(db_client)
    telegram = TelegramService()
    creds = CredentialsManager()
    
    # Получаем chat_id из Supabase
    telegram_creds = creds.load_credentials('telegram')
    channel_id = telegram_creds['channel_id']  # Используем channel_id вместо chat_id
    print(f"Channel ID: {channel_id}")
    
    # Получаем даты для сравнения
    start_date = datetime(2023, 12, 11).date()
    end_date = datetime(2024, 12, 6).date()
    
    # Получаем изменения позиций
    changes, stats = analyzer.get_position_changes(start_date, end_date)
    print(f"\nИзменения: {changes}")
    print(f"\nСтатистика: {stats}")
    
    # Если нет изменений, отправляем сообщение об этом
    if not changes:
        message = (
            f"🔍 *Отчет по изменениям позиций*\n"
            f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n\n"
            f"За указанный период значимых изменений позиций не обнаружено."
        )
        telegram.send_message(channel_id, message, parse_mode='Markdown')
        return
    
    # Форматируем отчет
    report = (
        f"🔍 *Отчет по изменениям позиций*\n"
        f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n\n"
    )
    
    # Добавляем статистику
    report += (
        f"📊 *Общая статистика:*\n"
        f"Всего запросов: {stats.total_queries}\n"
        f"Значимых изменений: {stats.significant_changes}\n"
        f"Улучшений: {stats.improved_count}\n"
        f"Ухудшений: {stats.declined_count}\n"
        f"Средняя позиция: {stats.avg_position:.2f}\n\n"
    )
    
    # Добавляем детали изменений
    report += format_position_changes(changes[:10])  # Показываем топ-10 изменений
    
    # Отправляем отчет
    telegram.send_message(channel_id, report, parse_mode='Markdown')


if __name__ == '__main__':
    main()
