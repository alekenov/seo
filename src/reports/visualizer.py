"""
Модуль для создания визуализаций для отчетов.
Использует matplotlib для генерации графиков.
"""

import io
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

class ReportVisualizer:
    """Класс для создания визуализаций для отчетов."""
    
    def __init__(self):
        """Инициализация визуализатора."""
        # Настройка стиля для графиков
        plt.style.use('seaborn')
        # Настройка русского языка
        plt.rcParams['font.family'] = 'DejaVu Sans'
        
    def create_trend_chart(self, 
                          dates: List[datetime],
                          values: List[float],
                          title: str,
                          ylabel: str) -> bytes:
        """
        Создает график тренда метрики.
        
        Args:
            dates: Список дат
            values: Список значений
            title: Заголовок графика
            ylabel: Подпись оси Y
            
        Returns:
            bytes: PNG изображение графика
        """
        plt.figure(figsize=(10, 6))
        plt.plot(dates, values, marker='o')
        
        # Форматирование
        plt.title(title)
        plt.ylabel(ylabel)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Форматирование дат
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        plt.xticks(rotation=45)
        
        # Сохраняем график в байты
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        
        return buf.getvalue()
        
    def create_category_comparison(self,
                                 categories: Dict[str, Dict],
                                 metric: str,
                                 title: str) -> bytes:
        """
        Создает столбчатую диаграмму для сравнения категорий.
        
        Args:
            categories: Словарь с данными категорий
            metric: Название метрики для сравнения
            title: Заголовок графика
            
        Returns:
            bytes: PNG изображение графика
        """
        # Подготовка данных
        names = list(categories.keys())
        current_values = [cat[f'current_{metric}'] for cat in categories.values()]
        previous_values = [cat[f'previous_{metric}'] for cat in categories.values()]
        
        # Создание графика
        plt.figure(figsize=(12, 6))
        x = np.arange(len(names))
        width = 0.35
        
        plt.bar(x - width/2, current_values, width, label='Текущая неделя')
        plt.bar(x + width/2, previous_values, width, label='Прошлая неделя')
        
        # Форматирование
        plt.title(title)
        plt.xlabel('Категории')
        plt.ylabel(metric.capitalize())
        plt.xticks(x, names, rotation=45, ha='right')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.3)
        
        # Сохраняем график в байты
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        
        return buf.getvalue()
        
    def create_position_changes(self,
                              queries: List[Dict],
                              title: str = "Изменение позиций по запросам") -> bytes:
        """
        Создает график изменения позиций для топ запросов.
        
        Args:
            queries: Список словарей с данными запросов
            title: Заголовок графика
            
        Returns:
            bytes: PNG изображение графика
        """
        # Сортируем запросы по абсолютному изменению позиции
        queries = sorted(queries, 
                        key=lambda x: abs(x['position_change']),
                        reverse=True)[:10]
        
        # Подготовка данных
        names = [q['query'] for q in queries]
        current_pos = [q['current_position'] for q in queries]
        previous_pos = [q['previous_position'] for q in queries]
        
        # Создание графика
        plt.figure(figsize=(12, 6))
        x = np.arange(len(names))
        width = 0.35
        
        plt.bar(x - width/2, previous_pos, width, label='Прошлая неделя')
        plt.bar(x + width/2, current_pos, width, label='Текущая неделя')
        
        # Форматирование
        plt.title(title)
        plt.xlabel('Запросы')
        plt.ylabel('Позиция')
        plt.xticks(x, names, rotation=45, ha='right')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.3)
        
        # Инвертируем ось Y, так как меньшие позиции лучше
        plt.gca().invert_yaxis()
        
        # Сохраняем график в байты
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        
        return buf.getvalue()
