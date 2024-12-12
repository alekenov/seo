"""
Тестовый запуск аналитических модулей.
"""
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

# Добавляем путь к src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MockSupabaseClient:
    def __init__(self):
        self.test_data = pd.read_csv('dataset/test_data.csv')
        
    def execute_query(self, query: str, vars=None):
        return self.test_data.to_dict('records')

def format_number(num):
    """Форматирование чисел для вывода"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    if num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def main():
    # Инициализируем тестовый клиент
    db_client = MockSupabaseClient()
    
    # Создаем анализаторы
    from src.analytics.position_analysis import PositionAnalyzer
    from src.analytics.ctr_analysis import CTRAnalyzer
    from src.analytics.page_analysis import PageAnalyzer
    
    position_analyzer = PositionAnalyzer(db_client)
    ctr_analyzer = CTRAnalyzer(db_client)
    page_analyzer = PageAnalyzer(db_client)
    
    # Период анализа
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print("\n=== Анализ топ-10 позиций по трафику ===")
    print("-" * 50)
    
    # Получаем данные
    df = pd.read_csv('dataset/test_data.csv')
    
    if not df.empty:
        # Группируем по запросам
        top_queries = df.groupby('query').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'position': 'mean'
        }).sort_values('clicks', ascending=False).head(10)
        
        print("\nТоп-10 запросов по трафику:")
        print(f"{'Запрос':<30} {'Позиция':<10} {'Клики':<10} {'Показы':<10} {'CTR':<10}")
        print("-" * 70)
        
        for query, row in top_queries.iterrows():
            ctr = row['clicks'] / row['impressions'] * 100
            print(f"{query[:30]:<30} {row['position']:.1f}{'':3} {format_number(row['clicks']):<10} {format_number(row['impressions']):<10} {ctr:.1f}%")
            
        # Анализ CTR для топ-запросов
        print("\n=== Анализ CTR ===")
        print("-" * 50)
        
        for query, row in top_queries.iterrows():
            url_data = df[df['query'] == query].iloc[0]
            ctr_results = ctr_analyzer.analyze_ctr(url_data['url'])
            
            if ctr_results['status'] == 'success':
                print(f"\nЗапрос: {query}")
                print(f"URL: {url_data['url']}")
                print(f"Средний CTR: {ctr_results['stats']['avg_ctr']*100:.1f}%")
                
                if ctr_results['anomalies']:
                    print("Аномалии:")
                    for anomaly in ctr_results['anomalies']:
                        print(f"- Позиция {anomaly['position']}: {anomaly['type']}")
                        if 'expected_ctr' in anomaly:
                            print(f"  Ожидаемый CTR: {anomaly['expected_ctr']*100:.1f}%")
                            print(f"  Текущий CTR: {anomaly['actual_ctr']*100:.1f}%")
                
        # Анализ страниц
        print("\n=== Анализ эффективности страниц ===")
        print("-" * 50)
        
        unique_urls = df['url'].unique()
        for url in unique_urls[:5]:  # Анализируем топ-5 страниц
            page_results = page_analyzer.analyze_page(url)
            
            print(f"\nСтраница: {url}")
            
            if page_results['problems']:
                print("Проблемы:")
                for problem in page_results['problems']:
                    print(f"- [{problem['severity'].upper()}] {problem['description']}")
            
            if page_results.get('recommendations'):
                print("Рекомендации:")
                for rec in page_results['recommendations']:
                    print(f"- [{rec['priority'].upper()}] {rec['description']}")
                    print(f"  Ожидаемый эффект: {rec['expected_impact']}")
            
            potential = page_results['growth_potential']
            print(f"Потенциал роста трафика: {potential['traffic_potential']}%")
            if potential['priority_areas']:
                print("Приоритетные направления:")
                for area in potential['priority_areas']:
                    print(f"- {area['description']} (влияние: {area['impact']})")
    else:
        print("Нет данных за указанный период")

if __name__ == "__main__":
    main()
