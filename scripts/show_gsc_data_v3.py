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
        
        # Get search queries
        logger.info("Top 10 queries by clicks:")
        queries = collector.get_search_queries(start_date, end_date)
        if queries:
            sorted_queries = sorted(queries, key=lambda x: x.get('clicks', 0), reverse=True)[:10]
            print(tabulate(
                [[q.get('query', ''), q.get('clicks', 0), q.get('impressions', 0), 
                  round(q.get('ctr', 0) * 100, 2), round(q.get('position', 0), 2)] 
                 for q in sorted_queries],
                headers=['Query', 'Clicks', 'Impressions', 'CTR %', 'Position'],
                tablefmt='grid'
            ))
            print("\n")
        
        # Get pages
        logger.info("Top 10 pages by impressions:")
        pages = collector.get_pages(start_date, end_date)
        if pages:
            sorted_pages = sorted(pages, key=lambda x: x.get('impressions', 0), reverse=True)[:10]
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
            
        # Get CTR and clicks data
        logger.info("\nTop 10 queries by CTR (minimum 100 impressions):")
        ctr_data = collector.get_ctr_clicks(start_date, end_date)
        if ctr_data:
            # Filter queries with at least 100 impressions
            filtered_data = [d for d in ctr_data if d.get('impressions', 0) >= 100]
            sorted_ctr = sorted(filtered_data, key=lambda x: x.get('ctr', 0), reverse=True)[:10]
            print(tabulate(
                [[c.get('query', ''), round(c.get('ctr', 0) * 100, 2), 
                  c.get('clicks', 0), c.get('impressions', 0)]
                 for c in sorted_ctr],
                headers=['Query', 'CTR %', 'Clicks', 'Impressions'],
                tablefmt='grid'
            ))
            
    except Exception as e:
        logger.error(f"Error showing GSC data: {str(e)}")
        raise

if __name__ == "__main__":
    show_gsc_data()
