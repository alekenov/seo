from src.database.postgres_client import PostgresClient

def main():
    with PostgresClient().get_connection() as conn:
        with conn.cursor() as cur:
            # Проверяем структуру таблицы
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'search_queries_daily'
            """)
            print("\nСтруктура таблицы:")
            for column in cur.fetchall():
                print(f"- {column[0]}: {column[1]}")
            
            # Проверяем данные
            cur.execute("SELECT COUNT(*) FROM search_queries_daily")
            count = cur.fetchone()[0]
            print(f"\nВсего записей: {count}")
            
            if count > 0:
                cur.execute("SELECT * FROM search_queries_daily LIMIT 1")
                row = cur.fetchone()
                print("\nПример записи:")
                columns = [desc[0] for desc in cur.description]
                for i, value in enumerate(row):
                    print(f"- {columns[i]}: {value}")

if __name__ == "__main__":
    main()
