"""Configuration utilities for SEO data collector."""
import os
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

class Config:
    """Configuration manager."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load_config()
        self._load_env()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Error loading config: {str(e)}")
    
    def _load_env(self) -> None:
        """Load environment variables."""
        load_dotenv()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
