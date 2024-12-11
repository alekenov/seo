"""Google Search Console data collector."""
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Union, Any
import pandas as pd

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.collectors.base_collector import BaseCollector
from src.models.metrics import GSCMetric
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.utils.token_manager import TokenManager
from src.database.postgres_client import PostgresClient

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
        self.token_manager = TokenManager()
        self.db = PostgresClient()
        self.connect()
    
    def connect(self) -> bool:
        """Establish connection to GSC API."""
        try:
            # Define the required scopes
            SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
            
            # Try to load existing token
            token_data = self.token_manager.load_token('gsc')
            credentials = None
            
            if token_data:
                credentials = self.token_manager.create_credentials(token_data)
            
            # If no valid token found, run OAuth2 flow
            if not credentials:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'config/credentials.json', SCOPES)
                credentials = flow.run_local_server(port=0)
                
                # Save new token
                self.token_manager.save_token('gsc', credentials)
            
            # Build the service
            self.service = build('searchconsole', 'v1', credentials=credentials)
            logger.info(f"Successfully connected to GSC for {self.site_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to GSC: {str(e)}")
            return False
    
    def collect(
        self,
        start_date: Union[str, datetime, date],
        end_date: Union[str, datetime, date],
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
            elif isinstance(start_date, date):
                start_date = start_date.strftime('%Y-%m-%d')
                
            if isinstance(end_date, datetime):
                end_date = end_date.strftime('%Y-%m-%d')
            elif isinstance(end_date, date):
                end_date = end_date.strftime('%Y-%m-%d')
            
            # Default dimensions if none provided
            dimensions = dimensions or ['query', 'page']
            
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
            
            processed_rows = []
            for row in rows:
                # Create a new row with all data
                processed_row = {
                    'clicks': row.get('clicks', 0),
                    'impressions': row.get('impressions', 0),
                    'ctr': row.get('ctr', 0.0),
                    'position': row.get('position', 0.0),
                }
                
                # Add dimension values
                for i, dimension in enumerate(dimensions):
                    processed_row[dimension] = row['keys'][i]
                
                processed_rows.append(processed_row)
            
            logger.info(
                f"Successfully collected {len(processed_rows)} "
                f"rows of data from {start_date} to {end_date}"
            )
            
            return processed_rows
            
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
                    date=None,  
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
    
    def save_to_database(
        self,
        metrics: List[Dict[str, Any]],
        city: Optional[str] = None
    ) -> bool:
        """Save metrics to PostgreSQL database.
        
        Args:
            metrics: List of metric dictionaries
            city: Optional city name for the metrics
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare metrics for database
            db_metrics = []
            for metric in metrics:
                db_metric = {
                    'date': metric.get('date') or datetime.now().date(),
                    'query': metric['query'],
                    'clicks': metric.get('clicks', 0),
                    'impressions': metric.get('impressions', 0),
                    'position': metric.get('position', 0.0),
                    'ctr': metric.get('ctr', 0.0),
                    'url': metric.get('url'),
                    'city': city
                }
                db_metrics.append(db_metric)
            
            # Insert into database
            self.db.insert_daily_metrics(db_metrics)
            logger.info(f"Successfully saved {len(metrics)} metrics to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving metrics to database: {e}")
            return False

    def save(self, data: List[Dict[str, Any]], filepath: str) -> bool:
        """Save processed data to file.
        
        This is an implementation of the abstract method from BaseCollector.
        For database operations, use save_to_database instead.
        
        Args:
            data: List of data to save
            filepath: Path to save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            logger.info(f"Successfully saved {len(data)} records to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving data to file: {e}")
            return False

    def get_metrics_for_period(
        self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        city: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get metrics from database for specified period.
        
        Args:
            start_date: Start date
            end_date: End date
            city: Optional city name to filter by
            
        Returns:
            List of metrics
        """
        try:
            # Convert dates if needed
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            elif isinstance(start_date, datetime):
                start_date = start_date.date()
                
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            elif isinstance(end_date, datetime):
                end_date = end_date.date()
            
            return self.db.get_metrics_by_date_range(
                start_date=start_date,
                end_date=end_date,
                city_name=city
            )
            
        except Exception as e:
            logger.error(f"Error getting metrics from database: {e}")
            return []

    def get_search_queries(
        self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        row_limit: int = 1000,
        country: Optional[str] = None,
        device: Optional[str] = None
    ) -> List[Dict]:
        """Get search query data from GSC.
        
        Args:
            start_date: Start date for data collection
            end_date: End date for data collection
            row_limit: Maximum number of rows to return
            country: Filter by country (e.g., 'usa')
            device: Filter by device type (e.g., 'MOBILE', 'DESKTOP', 'TABLET')
            
        Returns:
            List of search query data
        """
        dimensions = ['query']
        filters = []
        
        if country:
            filters.append({
                'dimension': 'country',
                'operator': 'equals',
                'expression': country.upper()
            })
            
        if device:
            filters.append({
                'dimension': 'device',
                'operator': 'equals',
                'expression': device.upper()
            })
            
        return self.collect(
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions,
            filters=filters,
            row_limit=row_limit
        )
    
    def get_pages(
        self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        row_limit: int = 1000,
        country: Optional[str] = None
    ) -> List[Dict]:
        """Get page performance data from GSC.
        
        Args:
            start_date: Start date for data collection
            end_date: End date for data collection
            row_limit: Maximum number of rows to return
            country: Filter by country (e.g., 'usa')
            
        Returns:
            List of page performance data
        """
        dimensions = ['page']
        filters = []
        
        if country:
            filters.append({
                'dimension': 'country',
                'operator': 'equals',
                'expression': country.upper()
            })
            
        return self.collect(
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions,
            filters=filters,
            row_limit=row_limit
        )
    
    def get_position_metrics(
        self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        url: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[Dict]:
        """Get position metrics for specific URLs or queries.
        
        Args:
            start_date: Start date for data collection
            end_date: End date for data collection
            url: Filter by specific URL
            query: Filter by specific search query
            
        Returns:
            List of position metrics
        """
        dimensions = ['page', 'query']
        filters = []
        
        if url:
            filters.append({
                'dimension': 'page',
                'operator': 'equals',
                'expression': url
            })
            
        if query:
            filters.append({
                'dimension': 'query',
                'operator': 'equals',
                'expression': query
            })
            
        return self.collect(
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions,
            filters=filters
        )
    
    def get_ctr_clicks(
        self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        min_clicks: Optional[int] = None,
        min_position: Optional[float] = None
    ) -> List[Dict]:
        """Get CTR and clicks data with optional filtering.
        
        Args:
            start_date: Start date for data collection
            end_date: End date for data collection
            min_clicks: Minimum number of clicks to include
            min_position: Maximum position to include (e.g., 10.0 for first page)
            
        Returns:
            List of CTR and clicks data
        """
        data = self.collect(
            start_date=start_date,
            end_date=end_date,
            dimensions=['query', 'page']
        )
        
        # Filter results
        filtered_data = []
        for row in data:
            if min_clicks and row.get('clicks', 0) < min_clicks:
                continue
            if min_position and row.get('position', 100.0) > min_position:
                continue
            filtered_data.append(row)
            
        return filtered_data
