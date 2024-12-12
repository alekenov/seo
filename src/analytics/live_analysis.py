import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.collectors.gsc_collector import GSCCollector
from src.utils.config import Config
from src.analytics.position_analysis import PositionAnalyzer
from src.analytics.ctr_analysis import CTRAnalyzer
from src.analytics.page_analysis import PageAnalyzer
from src.database.supabase_client import SupabaseClient

class LiveAnalyzer:
    def __init__(self):
        # Инициализация Supabase клиента
        self.db_client = SupabaseClient()
        
        # Инициализация GSC коллектора
        self.gsc = GSCCollector('sc-domain:cvety.kz', Config())
        
        # Инициализация анализаторов
        self.position_analyzer = PositionAnalyzer(db_client=self.db_client)
        self.ctr_analyzer = CTRAnalyzer(db_client=self.db_client)
        self.page_analyzer = PageAnalyzer(db_client=self.db_client)
    
    def analyze_live_data(self, days=30):
        """Анализ реальных данных за указанный период"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        print(f"\n=== Анализ данных с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')} ===")
        print("--------------------------------------------------\n")
        
        # Получение данных из Search Console
        search_data = self.gsc.get_search_queries(
            start_date=start_date,
            end_date=end_date,
            row_limit=1000
        )
        
        # Получение данных по страницам
        page_data = self.gsc.get_pages(
            start_date=start_date,
            end_date=end_date,
            row_limit=1000
        )
        
        # Получение данных по позициям
        position_data = self.gsc.get_position_metrics(
            start_date=start_date,
            end_date=end_date
        )
        
        # Анализ позиций
        position_results = self.position_analyzer.analyze_positions(position_data)
        print("=== Анализ топ позиций по трафику ===")
        print("--------------------------------------------------\n")
        print(position_results)
        
        # Анализ CTR
        ctr_results = self.ctr_analyzer.analyze_ctr(search_data)
        print("\n=== Анализ CTR ===")
        print("--------------------------------------------------\n")
        print(ctr_results)
        
        # Анализ страниц
        page_results = self.page_analyzer.analyze_pages(page_data)
        print("\n=== Анализ эффективности страниц ===")
        print("--------------------------------------------------\n")
        print(page_results)
        
        # Сохранение результатов в базу данных
        self.save_analysis_results(position_results, ctr_results, page_results)
    
    def save_analysis_results(self, position_results, ctr_results, page_results):
        """Сохранение результатов анализа в PostgreSQL"""
        timestamp = datetime.now().isoformat()
        
        with self.db_client.cursor() as cursor:
            cursor.execute("""
                INSERT INTO seo_analysis (timestamp, position_analysis, ctr_analysis, page_analysis)
                VALUES (%s, %s, %s, %s)
            """, (timestamp, json.dumps(position_results), json.dumps(ctr_results), json.dumps(page_results)))
            
        self.db_client.commit()
        print("\nРезультаты анализа сохранены в базу данных.")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='SEO Analytics Tool')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')
    
    args = parser.parse_args()
    
    analyzer = LiveAnalyzer()
    analyzer.analyze_live_data(args.days)
