"""Base collector module for SEO data collection."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseCollector(ABC):
    """Abstract base class for all data collectors."""
    
    def __init__(self):
        """Initialize base collector."""
        self.data: Dict[str, Any] = {}
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to data source."""
        pass
    
    @abstractmethod
    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Collect data from source."""
        pass
    
    @abstractmethod
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process collected data."""
        pass
    
    @abstractmethod
    def save(self, data: List[Dict[str, Any]], filepath: str) -> bool:
        """Save processed data."""
        pass
