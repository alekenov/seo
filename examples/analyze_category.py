"""
Пример использования аналитических модулей.
"""
import os
from dotenv import load_dotenv
from src.database.supabase_client import SupabaseClient
from src.analytics.analyzer import SEOAnalyzer

def main():
    # Загружаем переменные окружения
    load_dotenv()
    
    # Инициализируем клиент базы данных
    db_client = SupabaseClient(
        url=os.getenv('SUPABASE_URL'),
        key=os.getenv('SUPABASE_KEY')
    )
    
    # Создаем анализатор
    analyzer = SEOAnalyzer(db_client)
    
    # Анализируем категорию
    category = "доставка цветов"
    results = analyzer.analyze_category(category, days=30)
    
    # Выводим результаты
    print(f"\nАнализ категории: {category}")
    print("-" * 50)
    
    # Общая статистика
    print("\nОбщая статистика:")
    print(f"Всего проблем: {results['summary']['metrics']['total_problems']}")
    print(f"Возможностей роста: {results['summary']['metrics']['total_opportunities']}")
    print(f"Затронуто URL: {results['summary']['metrics']['affected_urls']}")
    print(f"Критических проблем: {results['summary']['metrics']['critical_issues']}")
    
    # Топ рекомендаций
    print("\nПриоритетные рекомендации:")
    for i, rec in enumerate(results['summary']['top_recommendations'], 1):
        print(f"{i}. [{rec['priority'].upper()}] {rec['description']}")
        if 'expected_impact' in rec:
            print(f"   Ожидаемый эффект: {rec['expected_impact']}")
            
    # Детальный анализ позиций
    print("\nАнализ позиций:")
    trends = results['position_analysis']['trends']
    print(f"Улучшаются: {len(trends['improving'])} запросов")
    print(f"Ухудшаются: {len(trends['declining'])} запросов")
    print(f"Стабильны: {len(trends['stable'])} запросов")
    
    # Проблемные страницы
    print("\nПроблемные страницы:")
    for url, analysis in results['page_analysis'].items():
        if analysis['problems']:
            print(f"\n{url}:")
            for problem in analysis['problems']:
                print(f"- [{problem['severity'].upper()}] {problem['description']}")
                
if __name__ == "__main__":
    main()
