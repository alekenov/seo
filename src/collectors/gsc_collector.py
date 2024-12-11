"""Google Search Console data collector."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import pandas as pd

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.collectors.base_collector import BaseCollector
from src.models.metrics import GSCMetric
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class GSCCollector(BaseCollector):
    """Collector for Google Search Console data."""
    
    def __init__(self, site_url: str, config: Optional[Config] = None):
        """Initialize GSC collector.
        
        Args:
            site_url: URL of the site in GSC (e.g., 'sc-domain:example.com')
            config: Configuration object
        """
        super().__init__()
        self.site_url = site_url
        self.config = config or Config()
        self.service = None
        self.connect()
    
    def connect(self) -> bool:
        """Establish connection to GSC API."""
        try:
            # Define the required scopes
            SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
            
            # Initialize the OAuth2 flow
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES)
            
            # Run the OAuth2 flow
            credentials = flow.run_local_server(port=0)
            
            # Build the service
            self.service = build('searchconsole', 'v1', credentials=credentials)
            logger.info(f"Successfully connected to GSC for {self.site_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to GSC: {str(e)}")
            return False
    
    def collect(
        self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        dimensions: List[str] = None,
        filters: List[Dict] = None,
        row_limit: int = 1000,
    ) -> List[Dict]:
        """Collect data from GSC.
        
        Args:
            start_date: Start date for data collection
            end_date: End date for data collection
            dimensions: List of dimensions (e.g., ['query', 'page'])
            filters: List of dimension filters
            row_limit: Maximum number of rows to return
            
        Returns:
            List of data rows from GSC
        """
        try:
            # Convert dates to string format if needed
            if isinstance(start_date, datetime):
                start_date = start_date.strftime('%Y-%m-%d')
            if isinstance(end_date, datetime):
                end_date = end_date.strftime('%Y-%m-%d')
            
            # Default dimensions if none provided
            dimensions = dimensions or ['query', 'page']  # Убираем date из измерений
            
            # Prepare request body
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': dimensions,
                'rowLimit': row_limit
            }
            
            # Add filters if provided
            if filters:
                request['dimensionFilterGroups'] = [{
                    'filters': filters
                }]
            
            # Execute request
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url,
                body=request
            ).execute()
            
            # Process rows
            rows = response.get('rows', [])
            if not rows:
                logger.warning("No data returned from GSC API")
                return []
            
            for row in rows:
                # Extract dimensions in order
                row['query'] = row['keys'][0]
                row['url'] = row['keys'][1]
            
            logger.info(
                f"Successfully collected {len(rows)} "
                f"rows of data from {start_date} to {end_date}"
            )
            
            return rows
            
        except Exception as e:
            logger.error(f"Error collecting data from GSC: {str(e)}")
            return []
    
    def process(self, data: List[Dict]) -> List[GSCMetric]:
        """Process collected data into metrics.
        
        Args:
            data: Raw data from GSC
            
        Returns:
            List of processed GSC metrics
        """
        metrics = []
        try:
            for row in data:
                metric = GSCMetric(
                    date=None,  # Убираем дату
                    source='google_search_console',
                    metric_type='search_analytics',
                    value=row.get('clicks', 0),
                    clicks=row.get('clicks', 0),
                    impressions=row.get('impressions', 0),
                    ctr=row.get('ctr', 0.0),
                    position=row.get('position', 0.0),
                    query=row['query'],
                    url=row['url']
                )
                metrics.append(metric)
            
            logger.info(f"Successfully processed {len(metrics)} metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Error processing GSC data: {str(e)}")
            return []
    
    def save(self, data: List[GSCMetric], filepath: str) -> bool:
        """Save processed metrics to file.
        
        Args:
            data: List of GSC metrics to save
            filepath: Path to save the data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert metrics to dictionaries
            rows = [metric.to_dict() for metric in data]
            
            # Create DataFrame and save to CSV
            df = pd.DataFrame(rows)
            df.to_csv(filepath, index=False)
            
            logger.info(f"Successfully saved {len(rows)} metrics to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving GSC data: {str(e)}")
            return False
