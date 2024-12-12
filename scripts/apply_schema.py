"""
Скрипт для применения схемы базы данных.
"""
import os
import sys

# Добавляем корневую директорию проекта в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.database.postgres_client import PostgresClient

def apply_schema():
    """Применение схемы базы данных."""
    # Читаем SQL файл
    schema_path = os.path.join(project_root, 'src', 'database', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Подключаемся к базе данных и применяем схему
    db = PostgresClient()
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # Выполняем весь SQL как одну команду
            print("Применяем схему базы данных...")
            cur.execute(schema_sql)
    
    print("\nСхема базы данных успешно применена!")

if __name__ == "__main__":
    apply_schema()
