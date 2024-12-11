"""Test GSC Collector functionality."""

import os
import logging
from datetime import datetime, timedelta
from src.collectors.gsc_collector import GSCCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gsc_collector():
    """Test GSC Collector functionality."""
    try:
        # Initialize collector
        site_url = "sc-domain:cvety.kz"  # Используем доменное свойство
        collector = GSCCollector(site_url=site_url)
        
        # Set test parameters
        end_date = datetime(2024, 12, 11)  # Today
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        # Test search queries collection
        logger.info("Testing search queries collection...")
        queries_data = collector.get_search_queries(
            start_date=start_date,
            end_date=end_date
        )
        logger.info(f"Collected {len(queries_data)} search queries")
        
        # Test pages collection
        logger.info("Testing pages collection...")
        pages_data = collector.get_pages(
            start_date=start_date,
            end_date=end_date
        )
        logger.info(f"Collected {len(pages_data)} pages")
        
        # Test position metrics collection
        logger.info("Testing position metrics collection...")
        position_data = collector.get_position_metrics(
            start_date=start_date,
            end_date=end_date
        )
        logger.info(f"Collected {len(position_data)} position metrics")
        
        # Test CTR and clicks collection
        logger.info("Testing CTR and clicks collection...")
        ctr_data = collector.get_ctr_clicks(
            start_date=start_date,
            end_date=end_date
        )
        logger.info(f"Collected {len(ctr_data)} CTR/clicks metrics")
        
        # Test saving to database
        logger.info("Testing database save functionality...")
        collector.save_to_database(queries_data)
        collector.save_to_database(pages_data)
        collector.save_to_database(position_data)
        collector.save_to_database(ctr_data)
        logger.info("Successfully saved data to database")
        
        # Test retrieving metrics from database
        logger.info("Testing database retrieval functionality...")
        metrics = collector.get_metrics_for_period(
            start_date=start_date,
            end_date=end_date
        )
        logger.info(f"Retrieved {len(metrics)} metrics from database")
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        raise

if __name__ == "__main__":
    test_gsc_collector()
