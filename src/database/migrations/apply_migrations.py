import os
import sys

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.db import SupabaseDB

def main():
    """Применяет все SQL миграции из текущей директории."""
    db = SupabaseDB()
    
    # Получаем список всех SQL файлов в директории
    migration_files = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.sql')]
    migration_files.sort()  # Сортируем файлы по имени
    
    for file_name in migration_files:
        print(f"\nПрименяем миграцию {file_name}...")
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        
        with open(file_path, 'r') as f:
            sql = f.read()
            
        try:
            db.execute(sql)
            print(f"Миграция {file_name} успешно применена")
        except Exception as e:
            print(f"Ошибка при применении миграции {file_name}: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    main()
