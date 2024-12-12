"""
Модуль для анализа CTR и выявления аномалий.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from src.database.supabase_client import SupabaseClient

class CTRAnalyzer:
    def __init__(self, db_client: SupabaseClient):
        """
        Инициализация анализатора CTR.
        
        Args:
            db_client: Клиент для работы с базой данных
        """
        self.db = db_client
        # Средние значения CTR по позициям (базовые значения)
        self.baseline_ctr = {
            1: 0.25,  # 25% CTR для первой позиции
            2: 0.15,  # 15% для второй
            3: 0.10,  # 10% для третьей
            4: 0.08,
            5: 0.07,
            6: 0.06,
            7: 0.05,
            8: 0.04,
            9: 0.03,
            10: 0.02
        }
        
    def analyze_ctr(
        self,
        url: str,
        days: int = 30
    ) -> Dict:
        """
        Анализ CTR для конкретной страницы.
        
        Args:
            url: URL страницы
            days: Количество дней для анализа
            
        Returns:
            Словарь с результатами анализа
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Получаем данные по CTR
        query = f"""
        SELECT 
            query,
            position,
            clicks,
            impressions,
            date
        FROM search_analytics
        WHERE 
            url = '{url}'
            AND date BETWEEN '{start_date}' AND '{end_date}'
        """
        df = pd.DataFrame(self.db.execute_query(query))
        
        if df.empty:
            return {
                'status': 'error',
                'message': 'Нет данных для анализа'
            }
            
        # Добавляем CTR
        df['ctr'] = df['clicks'] / df['impressions']
        
        # Анализируем аномалии
        anomalies = self._find_ctr_anomalies(df)
        
        # Готовим рекомендации
        recommendations = self._generate_recommendations(df, anomalies)
        
        return {
            'status': 'success',
            'anomalies': anomalies,
            'recommendations': recommendations,
            'stats': {
                'avg_ctr': df['ctr'].mean(),
                'total_clicks': df['clicks'].sum(),
                'total_impressions': df['impressions'].sum()
            }
        }
        
    def _find_ctr_anomalies(self, df: pd.DataFrame) -> List[Dict]:
        """
        Поиск аномалий в CTR.
        """
        anomalies = []
        
        for position in range(1, 11):
            position_data = df[df['position'] == position]
            if position_data.empty:
                continue
                
            actual_ctr = position_data['ctr'].mean()
            expected_ctr = self.baseline_ctr.get(position, 0.01)
            
            # Если CTR значительно ниже ожидаемого
            if actual_ctr < expected_ctr * 0.7:  # Порог в 70% от ожидаемого
                anomalies.append({
                    'position': position,
                    'actual_ctr': actual_ctr,
                    'expected_ctr': expected_ctr,
                    'type': 'low_ctr',
                    'impact': (expected_ctr - actual_ctr) * position_data['impressions'].mean()
                })
                
            # Если CTR нестабильный
            if self._is_unstable_ctr(position_data['ctr']):
                anomalies.append({
                    'position': position,
                    'type': 'unstable_ctr',
                    'impact': position_data['impressions'].mean() * 0.1  # Примерная оценка потерь
                })
                
        return sorted(anomalies, key=lambda x: x['impact'], reverse=True)
        
    def _is_unstable_ctr(self, ctr_series: pd.Series, threshold: float = 0.5) -> bool:
        """
        Проверка на нестабильность CTR.
        """
        if len(ctr_series) < 3:
            return False
            
        # Считаем коэффициент вариации
        cv = ctr_series.std() / ctr_series.mean()
        return cv > threshold
        
    def _generate_recommendations(
        self,
        df: pd.DataFrame,
        anomalies: List[Dict]
    ) -> List[Dict]:
        """
        Генерация рекомендаций по улучшению CTR.
        """
        recommendations = []
        
        for anomaly in anomalies:
            if anomaly['type'] == 'low_ctr':
                recommendations.append({
                    'type': 'title_optimization',
                    'priority': 'high' if anomaly['position'] <= 3 else 'medium',
                    'description': f'Оптимизировать заголовок для позиции {anomaly["position"]}',
                    'expected_impact': f'+{int(anomaly["impact"])} кликов'
                })
                
                recommendations.append({
                    'type': 'description_optimization',
                    'priority': 'medium',
                    'description': 'Улучшить мета-описание',
                    'expected_impact': 'Увеличение CTR на 20-30%'
                })
                
            elif anomaly['type'] == 'unstable_ctr':
                recommendations.append({
                    'type': 'content_relevance',
                    'priority': 'high',
                    'description': 'Проверить соответствие контента поисковым запросам',
                    'expected_impact': 'Стабилизация CTR'
                })
                
        return recommendations
