from src.database.postgres_client import PostgresClient
from datetime import datetime, date

def main():
    start_date = date(2023, 12, 11)
    end_date = date(2024, 12, 6)
    
    with PostgresClient().get_connection() as conn:
        with conn.cursor() as cur:
            # Проверяем базовый запрос
            query = """
            WITH position_data AS (
                SELECT 
                    sq.query,
                    sq.page_url,
                    sq.city,
                    sq.position,
                    sq.impressions,
                    sq.clicks,
                    sq.query_type,
                    sq.date
                FROM search_queries_daily sq
                WHERE sq.date BETWEEN %s AND %s
            )
            SELECT 
                pd1.query,
                pd1.page_url,
                pd1.city,
                pd1.position as old_position,
                pd2.position as new_position,
                pd1.impressions as old_impressions,
                pd2.impressions as new_impressions,
                pd1.clicks as old_clicks,
                pd2.clicks as new_clicks,
                pd1.query_type,
                pd1.date as old_date,
                pd2.date as new_date
            FROM position_data pd1
            JOIN position_data pd2 
                ON pd1.query = pd2.query 
                AND pd1.page_url = pd2.page_url 
                AND COALESCE(pd1.city, '') = COALESCE(pd2.city, '')
            WHERE pd1.date = %s 
                AND pd2.date = %s
            ORDER BY pd1.query, pd1.page_url, pd1.city
            """
            
            params = [start_date, end_date, start_date, end_date]
            cur.execute(query, params)
            rows = cur.fetchall()
            
            print(f"\nНайдено строк: {len(rows)}")
            if rows:
                print("\nПервые 5 строк:")
                for row in rows[:5]:
                    print(row)
            
            # Проверяем данные по датам
            print("\nПроверяем данные по датам:")
            cur.execute("""
                SELECT date, COUNT(*) 
                FROM search_queries_daily 
                WHERE date IN (%s, %s)
                GROUP BY date
                ORDER BY date
            """, [start_date, end_date])
            
            for row in cur.fetchall():
                print(f"- {row[0]}: {row[1]} записей")

if __name__ == "__main__":
    main()
