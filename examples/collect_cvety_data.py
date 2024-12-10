"""Example script for collecting data from cvety.kz."""
import os
from datetime import datetime, timedelta
from src.collectors.gsc_collector import GSCCollector
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Collect and analyze data for cvety.kz."""
    # Initialize collector
    site_url = 'sc-domain:cvety.kz'
    collector = GSCCollector(site_url)
    
    # Set date range (last 30 days)
    end_date = datetime.now().date().strftime('%Y-%m-%d')
    start_date = (datetime.now().date() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Collect data
    logger.info(f"Collecting data from {start_date} to {end_date}")
    
    # Get overall metrics
    data = collector.collect(
        start_date=start_date,
        end_date=end_date,
        dimensions=['query', 'page'],
        row_limit=1000
    )
    
    # Process data
    metrics = collector.process(data)
    
    # Save data to CSV
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    filename = f"gsc_data_{start_date}_{end_date}.csv"
    filepath = os.path.join(data_dir, filename)
    collector.save(metrics, filepath)
    
    # Print some insights
    print("\nTop Queries by Clicks:")
    print("-" * 50)
    for metric in sorted(metrics, key=lambda x: x.clicks, reverse=True)[:10]:
        print(f"Query: {metric.query}")
        print(f"URL: {metric.url}")
        print(f"Clicks: {metric.clicks}")
        print(f"Position: {metric.position:.1f}")
        print(f"CTR: {metric.ctr:.2%}")
        print("-" * 50)

if __name__ == '__main__':
    main()
