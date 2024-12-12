"""
Основной интерфейс для аналитических модулей.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.database.supabase_client import SupabaseClient
from src.analytics.position_analysis import PositionAnalyzer
from src.analytics.ctr_analysis import CTRAnalyzer
from src.analytics.page_analysis import PageAnalyzer

class SEOAnalyzer:
    def __init__(self, db_client: SupabaseClient):
        """
        Инициализация основного анализатора.
        
        Args:
            db_client: Клиент для работы с базой данных
        """
        self.position_analyzer = PositionAnalyzer(db_client)
        self.ctr_analyzer = CTRAnalyzer(db_client)
        self.page_analyzer = PageAnalyzer(db_client)
        
    def analyze_category(
        self,
        category: str,
        days: int = 30
    ) -> Dict:
        """
        Комплексный анализ категории.
        
        Args:
            category: Категория для анализа
            days: Количество дней для анализа
            
        Returns:
            Словарь с результатами анализа
        """
        # Анализ позиций
        position_analysis = self.position_analyzer.analyze_category(
            category=category,
            days=days
        )
        
        # Анализ CTR для каждого URL в категории
        ctr_analysis = {}
        for url in position_analysis['affected_urls']:
            ctr_analysis[url] = self.ctr_analyzer.analyze_ctr(
                url=url,
                days=days
            )
            
        # Анализ страниц
        page_analysis = {}
        for url in position_analysis['affected_urls']:
            page_analysis[url] = self.page_analyzer.analyze_page(
                url=url,
                days=days
            )
            
        # Агрегируем результаты
        return {
            'category': category,
            'period': {
                'start': datetime.now() - timedelta(days=days),
                'end': datetime.now()
            },
            'position_analysis': position_analysis,
            'ctr_analysis': ctr_analysis,
            'page_analysis': page_analysis,
            'summary': self._generate_summary(
                position_analysis,
                ctr_analysis,
                page_analysis
            )
        }
        
    def _generate_summary(
        self,
        position_analysis: Dict,
        ctr_analysis: Dict,
        page_analysis: Dict
    ) -> Dict:
        """
        Генерация сводного отчета по всем метрикам.
        """
        # Считаем общие метрики
        total_problems = len(position_analysis.get('problems', []))
        total_opportunities = 0
        
        for url_analysis in page_analysis.values():
            total_problems += len(url_analysis.get('problems', []))
            potential = url_analysis.get('growth_potential', {})
            total_opportunities += len(potential.get('priority_areas', []))
            
        # Приоритизируем рекомендации
        all_recommendations = []
        
        # Добавляем рекомендации по позициям
        if 'trends' in position_analysis:
            if position_analysis['trends'].get('declining'):
                all_recommendations.append({
                    'priority': 'high',
                    'type': 'positions',
                    'description': 'Остановить падение позиций',
                    'affected_queries': len(position_analysis['trends']['declining'])
                })
                
        # Добавляем рекомендации по CTR
        for url, analysis in ctr_analysis.items():
            if analysis.get('status') == 'success':
                for anomaly in analysis.get('anomalies', []):
                    if anomaly['type'] == 'low_ctr':
                        all_recommendations.append({
                            'priority': 'high' if anomaly['position'] <= 3 else 'medium',
                            'type': 'ctr',
                            'description': f'Улучшить CTR для {url}',
                            'potential_clicks': int(anomaly['impact'])
                        })
                        
        # Добавляем рекомендации по страницам
        for url, analysis in page_analysis.items():
            for rec in analysis.get('recommendations', []):
                if rec['priority'] == 'high':
                    all_recommendations.append({
                        'priority': 'high',
                        'type': 'page',
                        'description': f'{rec["description"]} ({url})',
                        'expected_impact': rec['expected_impact']
                    })
                    
        # Сортируем рекомендации по приоритету
        all_recommendations.sort(
            key=lambda x: 0 if x['priority'] == 'high' else 1
        )
        
        return {
            'metrics': {
                'total_problems': total_problems,
                'total_opportunities': total_opportunities,
                'affected_urls': len(page_analysis),
                'critical_issues': len([r for r in all_recommendations 
                                     if r['priority'] == 'high'])
            },
            'top_recommendations': all_recommendations[:5],
            'status': 'critical' if total_problems > 5 else 'warning' 
                     if total_problems > 0 else 'good'
        }
