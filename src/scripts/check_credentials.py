"""Скрипт для проверки учетных данных."""

import psycopg2
from src.config.supabase_config import DATABASE_URL

def main():
    """Основная функция."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT service_name, key_name, key_value FROM credentials")
    rows = cur.fetchall()
    
    print("\nТекущие учетные данные:")
    for row in rows:
        service, key, value = row
        # Скрываем значение, если оно длиннее 50 символов
        if len(value) > 50:
            value = value[:47] + "..."
        print(f"{service}.{key}: {value}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
