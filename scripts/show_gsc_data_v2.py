"""Show examples of collected GSC data."""

import logging
from datetime import datetime, timedelta
from tabulate import tabulate
from src.collectors.gsc_collector import GSCCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_gsc_data():
    """Show examples of collected GSC data."""
    try:
        # Initialize collector
        site_url = "sc-domain:cvety.kz"
        collector = GSCCollector(site_url=site_url)
        
        # Set date range
        end_date = datetime(2024, 12, 11)  # Today
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        # Get query metrics
        logger.info("Top 10 queries by clicks:")
        query_metrics = collector.get_query_metrics(start_date, end_date)
        if query_metrics:
            sorted_queries = sorted(query_metrics, key=lambda x: x.get('clicks', 0), reverse=True)[:10]
            print(tabulate(
                [[q.get('query', ''), q.get('clicks', 0), q.get('impressions', 0), 
                  round(q.get('ctr', 0) * 100, 2), round(q.get('position', 0), 2)] 
                 for q in sorted_queries],
                headers=['Query', 'Clicks', 'Impressions', 'CTR %', 'Position'],
                tablefmt='grid'
            ))
            print("\n")
        
        # Get page metrics
        logger.info("Top 10 pages by impressions:")
        page_metrics = collector.get_page_metrics(start_date, end_date)
        if page_metrics:
            sorted_pages = sorted(page_metrics, key=lambda x: x.get('impressions', 0), reverse=True)[:10]
            print(tabulate(
                [[p.get('page', ''), p.get('impressions', 0), p.get('clicks', 0),
                  round(p.get('ctr', 0) * 100, 2), round(p.get('position', 0), 2)]
                 for p in sorted_pages],
                headers=['Page', 'Impressions', 'Clicks', 'CTR %', 'Position'],
                tablefmt='grid'
            ))
            print("\n")
        
        # Get position metrics
        logger.info("Top 10 queries by position (lowest position = highest ranking):")
        position_metrics = collector.get_position_metrics(start_date, end_date)
        if position_metrics:
            sorted_positions = sorted(position_metrics, key=lambda x: x.get('position', 100))[:10]
            print(tabulate(
                [[p.get('query', ''), round(p.get('position', 0), 2), p.get('clicks', 0),
                  p.get('impressions', 0), round(p.get('ctr', 0) * 100, 2)]
                 for p in sorted_positions],
                headers=['Query', 'Position', 'Clicks', 'Impressions', 'CTR %'],
                tablefmt='grid'
            ))
            
    except Exception as e:
        logger.error(f"Error showing GSC data: {str(e)}")
        raise

if __name__ == "__main__":
    show_gsc_data()
