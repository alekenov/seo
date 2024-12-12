"""
Модуль для анализа динамики позиций в поисковой выдаче.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
from src.database.supabase_client import SupabaseClient

class PositionAnalyzer:
    def __init__(self, db_client: SupabaseClient):
        """
        Инициализация анализатора позиций.
        
        Args:
            db_client: Клиент для работы с базой данных
        """
        self.db = db_client
        
    def get_position_changes(
        self,
        start_date: datetime,
        end_date: datetime,
        min_change: int = 5
    ) -> pd.DataFrame:
        """
        Получение изменений позиций за период.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            min_change: Минимальное изменение позиции для учета
            
        Returns:
            DataFrame с изменениями позиций
        """
        # Получаем данные из БД
        query = f"""
        SELECT 
            query,
            url,
            position,
            date
        FROM positions
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        """
        df = pd.DataFrame(self.db.execute_query(query))
        
        # Группируем по URL и запросу
        grouped = df.groupby(['url', 'query']).agg({
            'position': ['first', 'last', 'mean'],
            'date': ['min', 'max']
        }).reset_index()
        
        # Считаем изменение позиций
        grouped['position_change'] = grouped['position']['first'] - grouped['position']['last']
        
        # Фильтруем значимые изменения
        significant_changes = grouped[abs(grouped['position_change']) >= min_change]
        
        return significant_changes
        
    def analyze_category(
        self,
        category: str,
        days: int = 30
    ) -> Dict:
        """
        Анализ позиций для определенной категории.
        
        Args:
            category: Категория для анализа
            days: Количество дней для анализа
            
        Returns:
            Словарь с результатами анализа
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Получаем данные по категории
        query = f"""
        SELECT 
            p.query,
            p.url,
            p.position,
            p.date,
            c.category
        FROM positions p
        JOIN categories c ON p.url = c.url
        WHERE 
            c.category = '{category}'
            AND p.date BETWEEN '{start_date}' AND '{end_date}'
        """
        df = pd.DataFrame(self.db.execute_query(query))
        
        # Анализируем тренды
        trends = self._analyze_trends(df)
        
        # Находим проблемные запросы
        problems = self._find_problems(df)
        
        return {
            'trends': trends,
            'problems': problems,
            'affected_urls': df['url'].unique().tolist(),
            'period': {
                'start': start_date,
                'end': end_date
            }
        }
        
    def _analyze_trends(self, df: pd.DataFrame) -> Dict:
        """
        Анализ трендов в позициях.
        """
        trends = {
            'improving': [],
            'declining': [],
            'stable': []
        }
        
        # Группируем по URL и запросу
        for (url, query), group in df.groupby(['url', 'query']):
            # Считаем тренд
            trend = self._calculate_trend(group['position'].tolist())
            if trend < -0.5:  # Улучшение позиций
                trends['improving'].append({'url': url, 'query': query})
            elif trend > 0.5:  # Ухудшение позиций
                trends['declining'].append({'url': url, 'query': query})
            else:
                trends['stable'].append({'url': url, 'query': query})
                
        return trends
        
    def _find_problems(self, df: pd.DataFrame) -> List[Dict]:
        """
        Поиск проблемных запросов и страниц.
        """
        problems = []
        
        # Группируем по URL и запросу
        for (url, query), group in df.groupby(['url', 'query']):
            positions = group['position'].tolist()
            
            # Проверяем резкие падения
            if self._has_sudden_drop(positions):
                problems.append({
                    'url': url,
                    'query': query,
                    'type': 'sudden_drop',
                    'details': 'Резкое падение позиций'
                })
            
            # Проверяем нестабильность
            if self._is_unstable(positions):
                problems.append({
                    'url': url,
                    'query': query,
                    'type': 'unstable',
                    'details': 'Нестабильные позиции'
                })
                
        return problems
        
    def _calculate_trend(self, positions: List[float]) -> float:
        """
        Расчет тренда изменения позиций.
        Возвращает число от -1 до 1, где:
        -1 - сильное улучшение
        0 - стабильность
        1 - сильное ухудшение
        """
        if len(positions) < 2:
            return 0
            
        # Используем простую линейную регрессию
        x = list(range(len(positions)))
        y = positions
        
        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(len(x)))
        
        if denominator == 0:
            return 0
            
        slope = numerator / denominator
        
        # Нормализуем наклон до [-1, 1]
        return max(min(slope / 10, 1), -1)
        
    def _has_sudden_drop(self, positions: List[float], threshold: int = 10) -> bool:
        """
        Проверка на резкое падение позиций.
        """
        if len(positions) < 2:
            return False
            
        for i in range(1, len(positions)):
            if positions[i] - positions[i-1] >= threshold:
                return True
                
        return False
        
    def _is_unstable(self, positions: List[float], threshold: float = 5.0) -> bool:
        """
        Проверка на нестабильность позиций.
        """
        if len(positions) < 3:
            return False
            
        # Считаем стандартное отклонение
        mean = sum(positions) / len(positions)
        variance = sum((x - mean) ** 2 for x in positions) / len(positions)
        std_dev = variance ** 0.5
        
        return std_dev > threshold

    def analyze_positions(self, data: List[Dict]) -> Dict:
        """
        Анализ позиций на основе данных из GSC.
        
        Args:
            data: Данные из Google Search Console
            
        Returns:
            Словарь с результатами анализа
        """
        if not data:
            return {
                'top_queries': [],
                'position_changes': [],
                'problems': []
            }
            
        # Преобразуем данные в DataFrame
        df = pd.DataFrame(data)
        
        # Анализируем топ запросы
        top_queries = df.sort_values('clicks', ascending=False).head(10).to_dict('records')
        
        # Анализируем изменения позиций
        position_changes = []
        for _, row in df.iterrows():
            if 'position' in row and 'query' in row:
                position_changes.append({
                    'query': row['query'],
                    'position': row['position'],
                    'url': row.get('page', '')
                })
        
        # Находим проблемные запросы
        problems = []
        for _, row in df.iterrows():
            if row.get('position', 0) > 10:  # Позиция хуже 10
                problems.append({
                    'query': row['query'],
                    'position': row['position'],
                    'url': row.get('page', ''),
                    'type': 'bad_position',
                    'details': 'Позиция хуже 10'
                })
        
        return {
            'top_queries': top_queries,
            'position_changes': position_changes,
            'problems': problems
        }
