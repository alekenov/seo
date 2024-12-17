from src.database.postgres_client import PostgresClient
from datetime import date

def main():
    start_date = date(2023, 12, 11)
    end_date = date(2024, 12, 6)
    
    with PostgresClient().get_connection() as conn:
        with conn.cursor() as cur:
            # Проверяем запросы для каждой даты
            for check_date in [start_date, end_date]:
                print(f"\nЗапросы за {check_date}:")
                cur.execute("""
                    SELECT 
                        query,
                        city,
                        position,
                        clicks,
                        impressions,
                        query_type
                    FROM search_queries_daily
                    WHERE date = %s
                    ORDER BY clicks DESC
                    LIMIT 5
                """, [check_date])
                
                for row in cur.fetchall():
                    print(f"- {row[0]} ({row[1] or 'все города'}):")
                    print(f"  Позиция: {row[2]}")
                    print(f"  Клики: {row[3]}")
                    print(f"  Показы: {row[4]}")
                    print(f"  Тип: {row[5]}")
                    print()

if __name__ == "__main__":
    main()
