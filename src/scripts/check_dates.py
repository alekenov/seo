from src.database.postgres_client import PostgresClient

def main():
    with PostgresClient().get_connection() as conn:
        with conn.cursor() as cur:
            # Проверяем диапазон дат
            cur.execute("""
                SELECT 
                    MIN(date) as min_date,
                    MAX(date) as max_date,
                    COUNT(DISTINCT date) as unique_dates
                FROM search_queries_daily
            """)
            dates = cur.fetchone()
            print(f"\nДиапазон дат:")
            print(f"- Первая дата: {dates[0]}")
            print(f"- Последняя дата: {dates[1]}")
            print(f"- Уникальных дат: {dates[2]}")
            
            # Проверяем количество записей по датам
            cur.execute("""
                SELECT date, COUNT(*) as count
                FROM search_queries_daily
                GROUP BY date
                ORDER BY date DESC
                LIMIT 5
            """)
            print("\nПоследние 5 дат:")
            for row in cur.fetchall():
                print(f"- {row[0]}: {row[1]} записей")

if __name__ == "__main__":
    main()
