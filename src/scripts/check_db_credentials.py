"""Скрипт для проверки учетных данных в базе данных."""

from src.database.supabase_client import SupabaseClient
from src.utils.credentials_manager import CredentialsManager

def main():
    """Основная функция."""
    client = SupabaseClient()
    
    # Получаем данные из таблицы credentials
    result = client.client.table('credentials').select('*').execute()
    
    print("\nУчетные данные из базы данных:")
    for row in result.data:
        print(f"{row['service']}.{row['key']}: {row['value']}")
        
    # Проверяем значения через CredentialsManager
    cm = CredentialsManager()
    print("\nПроверка через CredentialsManager:")
    print(f"telegram.bot_token: {cm.get_credential('telegram', 'bot_token')}")
    print(f"telegram.channel_id: {cm.get_credential('telegram', 'channel_id')}")

if __name__ == '__main__':
    main()
