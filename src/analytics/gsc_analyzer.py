"""Google Search Console data analyzer."""
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union

import pandas as pd
import numpy as np

from src.models.metrics import GSCMetric
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Period(Enum):
    """Time period for data aggregation."""
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'


class Dimension(Enum):
    """Dimensions for data grouping."""
    DATE = 'date'
    QUERY = 'query'
    URL = 'url'
    DEVICE = 'device'
    COUNTRY = 'country'


class GSCAnalyzer:
    """Analyzer for Google Search Console data."""
    
    def __init__(self, metrics: List[GSCMetric]):
        """Initialize analyzer with GSC metrics.
        
        Args:
            metrics: List of GSC metrics to analyze
        """
        self.metrics = metrics
        self.df = self._prepare_dataframe()
    
    def _prepare_dataframe(self) -> pd.DataFrame:
        """Convert metrics to pandas DataFrame.
        
        Returns:
            DataFrame with processed metrics
        """
        # Convert metrics to dictionaries
        data = [metric.to_dict() for metric in self.metrics]
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate additional metrics
        df['clicks_per_impression'] = df['clicks'] / df['impressions']
        df['potential_clicks'] = df['impressions'] * df['ctr'].mean()
        df['click_opportunity'] = df['potential_clicks'] - df['clicks']
        
        # Add URL components
        df['url_path'] = df['url'].str.replace('https://cvety.kz', '')
        df['url_depth'] = df['url_path'].str.count('/')
        
        return df
    
    def aggregate_by_period(
        self,
        period: Period,
        dimensions: List[Dimension] = None,
        metrics: List[str] = None
    ) -> pd.DataFrame:
        """Aggregate data by specified period and dimensions.
        
        Args:
            period: Time period for aggregation
            dimensions: List of dimensions to group by
            metrics: List of metrics to aggregate
            
        Returns:
            Aggregated DataFrame
        """
        # Default dimensions
        if dimensions is None:
            dimensions = [Dimension.DATE]
        
        # Default metrics are all numeric columns
        if metrics is None:
            metrics = [
                'clicks', 'impressions', 'position', 'ctr',
                'clicks_per_impression', 'potential_clicks', 'click_opportunity'
            ]
        
        # Define period frequency
        freq_map = {
            Period.DAY: 'D',
            Period.WEEK: 'W',
            Period.MONTH: 'M'
        }
        freq = freq_map[period]
        
        # Set date as index for resampling
        df = self.df.set_index('date')
        
        # Prepare grouping dimensions
        group_by = []
        for dim in dimensions:
            if dim != Dimension.DATE:
                group_by.append(dim.value)
        
        # Define aggregation functions
        agg_funcs = {
            'clicks': 'sum',
            'impressions': 'sum',
            'position': 'mean',
            'ctr': 'mean',
            'clicks_per_impression': 'mean',
            'potential_clicks': 'sum',
            'click_opportunity': 'sum'
        }
        
        # Filter only requested metrics
        agg_funcs = {k: v for k, v in agg_funcs.items() if k in metrics}
        
        # Perform aggregation
        if group_by:
            # Group by dimensions first, then resample
            grouped = df.groupby(group_by + [pd.Grouper(freq=freq)]).agg(agg_funcs)
        else:
            # Only temporal aggregation
            grouped = df.resample(freq).agg(agg_funcs)
        
        # Calculate growth metrics
        if 'clicks' in metrics:
            grouped['clicks_growth'] = grouped['clicks'].pct_change() * 100
        if 'impressions' in metrics:
            grouped['impressions_growth'] = grouped['impressions'].pct_change() * 100
        if 'position' in metrics:
            grouped['position_change'] = grouped['position'].diff()
        
        return grouped
    
    def get_top_items(
        self,
        dimension: Dimension,
        metric: str = 'clicks',
        limit: int = 10,
        min_impressions: int = 100
    ) -> pd.DataFrame:
        """Get top performing items by dimension.
        
        Args:
            dimension: Dimension to analyze
            metric: Metric to sort by
            limit: Number of items to return
            min_impressions: Minimum impressions threshold
            
        Returns:
            DataFrame with top items
        """
        # Group by dimension
        grouped = self.df[self.df['impressions'] >= min_impressions].groupby(
            dimension.value
        ).agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'position': 'mean',
            'ctr': 'mean',
            'clicks_per_impression': 'mean',
            'potential_clicks': 'sum',
            'click_opportunity': 'sum'
        })
        
        # Sort by metric
        sorted_data = grouped.sort_values(metric, ascending=False)
        
        # Add ranks
        sorted_data['rank'] = range(1, len(sorted_data) + 1)
        
        return sorted_data.head(limit)
    
    def get_trending_items(
        self,
        dimension: Dimension,
        period: Period = Period.WEEK,
        metric: str = 'clicks',
        limit: int = 10,
        min_change_pct: float = 10.0,
        min_current_value: float = 5.0
    ) -> pd.DataFrame:
        """Get trending items by dimension.
        
        Args:
            dimension: Dimension to analyze
            period: Time period for trend calculation
            metric: Metric to analyze
            limit: Number of items to return
            min_change_pct: Minimum change percentage
            min_current_value: Minimum value for the metric in current period
            
        Returns:
            DataFrame with trending items
        """
        # Aggregate data by period and dimension
        aggregated = self.aggregate_by_period(
            period=period,
            dimensions=[dimension],
            metrics=[metric]
        )
        
        # Calculate period over period changes
        changes = pd.DataFrame()
        changes[metric] = aggregated[metric]
        changes[f'{metric}_change'] = changes[metric].pct_change() * 100
        
        # Create results DataFrame
        results = pd.DataFrame({
            'current_value': changes[metric],
            'previous_value': changes[metric].shift(1),
            'change_pct': changes[f'{metric}_change']
        })
        
        # Filter by minimum current value and significant changes
        results = results[
            (results['current_value'] >= min_current_value) &
            (abs(results['change_pct']) >= min_change_pct)
        ]
        
        # Sort by absolute change
        results['abs_change'] = abs(results['change_pct'])
        results = results.sort_values('abs_change', ascending=False)
        results = results.drop('abs_change', axis=1)
        
        return results.head(limit)
    
    def get_missed_opportunities(
        self,
        dimension: Dimension,
        limit: int = 10,
        min_impressions: int = 100
    ) -> pd.DataFrame:
        """Get items with highest potential for improvement.
        
        Args:
            dimension: Dimension to analyze
            limit: Number of items to return
            min_impressions: Minimum impressions threshold
            
        Returns:
            DataFrame with opportunities
        """
        # Group by dimension
        grouped = self.df[self.df['impressions'] >= min_impressions].groupby(
            dimension.value
        ).agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'position': 'mean',
            'ctr': 'mean',
            'click_opportunity': 'sum'
        })
        
        # Calculate potential improvement
        grouped['improvement_potential'] = (
            grouped['click_opportunity'] / grouped['clicks'] * 100
        )
        
        # Sort by improvement potential
        opportunities = grouped.sort_values('improvement_potential', ascending=False)
        
        return opportunities.head(limit)
    
    def get_seasonal_trends(
        self,
        dimension: Dimension,
        metric: str = 'clicks',
        period: Period = Period.MONTH,
        min_value: float = 10.0
    ) -> pd.DataFrame:
        """Get seasonal trends by analyzing monthly patterns.
        
        Args:
            dimension: Dimension to analyze
            metric: Metric to analyze
            period: Time period for aggregation
            min_value: Minimum value for the metric
            
        Returns:
            DataFrame with seasonal patterns
        """
        # Aggregate data by period and dimension
        aggregated = self.aggregate_by_period(
            period=period,
            dimensions=[dimension],
            metrics=[metric]
        )
        
        # Extract month from date index
        aggregated['month'] = aggregated.index.get_level_values('date').month
        
        # Reset index to make dimension column available
        aggregated = aggregated.reset_index()
        
        # Calculate monthly averages and standard deviations
        monthly_stats = aggregated.groupby(['month', dimension.value])[metric].agg([
            'mean',
            'std',
            'count'
        ]).reset_index()
        
        # Filter by minimum value and sample size
        monthly_stats = monthly_stats[
            (monthly_stats['mean'] >= min_value) &
            (monthly_stats['count'] >= 2)  # At least 2 data points per month
        ]
        
        # Calculate coefficient of variation
        monthly_stats['cv'] = monthly_stats['std'] / monthly_stats['mean']
        
        # Sort by variability
        monthly_stats = monthly_stats.sort_values('cv', ascending=False)
        
        return monthly_stats
    
    def calculate_trends(
        self,
        period: Period,
        metrics: List[str] = None,
        min_change_pct: float = 5.0
    ) -> Dict:
        """Calculate trends for specified metrics.
        
        Args:
            period: Time period for trend calculation
            metrics: List of metrics to analyze
            min_change_pct: Minimum change percentage to consider
            
        Returns:
            Dictionary with trend analysis
        """
        # Get aggregated data
        df = self.aggregate_by_period(period, metrics=metrics)
        
        # Calculate period over period changes
        changes = df.pct_change() * 100
        
        # Filter significant changes
        significant = changes[changes.abs() >= min_change_pct]
        
        # Prepare trends report
        trends = {
            'positive': {},
            'negative': {},
            'stable': {}
        }
        
        for metric in df.columns:
            # Get last change
            last_change = changes[metric].iloc[-1]
            
            if pd.isna(last_change):
                continue
                
            if abs(last_change) < min_change_pct:
                trends['stable'][metric] = {
                    'change_pct': last_change,
                    'current_value': df[metric].iloc[-1],
                    'previous_value': df[metric].iloc[-2]
                }
            elif last_change > 0:
                trends['positive'][metric] = {
                    'change_pct': last_change,
                    'current_value': df[metric].iloc[-1],
                    'previous_value': df[metric].iloc[-2]
                }
            else:
                trends['negative'][metric] = {
                    'change_pct': last_change,
                    'current_value': df[metric].iloc[-1],
                    'previous_value': df[metric].iloc[-2]
                }
        
        return trends
