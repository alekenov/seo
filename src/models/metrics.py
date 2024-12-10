"""Models for SEO metrics."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SEOMetric:
    """Base class for SEO metrics."""
    
    date: datetime
    source: str
    metric_type: str
    value: float
    
    def to_dict(self) -> dict:
        """Convert metric to dictionary."""
        return {
            'date': self.date.isoformat(),
            'source': self.source,
            'metric_type': self.metric_type,
            'value': self.value
        }

@dataclass
class GSCMetric(SEOMetric):
    """Google Search Console metric."""
    
    clicks: int
    impressions: int
    ctr: float
    position: float
    url: Optional[str] = None
    query: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert GSC metric to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            'clicks': self.clicks,
            'impressions': self.impressions,
            'ctr': self.ctr,
            'position': self.position,
            'url': self.url,
            'query': self.query
        })
        return base_dict
