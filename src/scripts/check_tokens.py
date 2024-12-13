"""
Скрипт для проверки токенов в базе данных
"""
import os
import sys
from datetime import datetime

# Добавляем корневую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient
from src.utils.token_manager import TokenManager

def main():
    """Проверка токенов."""
    token_manager = TokenManager()
    
    # Проверяем токен GSC
    token_data = token_manager.load_token('gsc')
    if token_data:
        print("\n=== Токен GSC найден ===")
        expiry = datetime.fromisoformat(token_data['expiry']) if token_data.get('expiry') else None
        print(f"Срок действия до: {expiry}")
    else:
        print("\n=== Токен GSC не найден ===")

if __name__ == "__main__":
    main()
