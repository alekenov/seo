"""Test script for GSC Collector functionality."""

from datetime import datetime, timedelta
import logging

from src.collectors.gsc_collector import GSCCollector
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def test_gsc_collector():
    """Test GSC Collector functionality."""
    try:
        # Initialize collector
        site_url = "sc-domain:cvety.kz"  # Замените на ваш домен
        collector = GSCCollector(site_url)
        
        # Test dates
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        logger.info("Testing search queries collection...")
        # Test getting search queries with device filter
        queries_mobile = collector.get_search_queries(
            start_date=start_date,
            end_date=end_date,
            device='MOBILE',
            row_limit=100
        )
        logger.info(f"Got {len(queries_mobile)} mobile search queries")
        
        # Save mobile queries to database
        collector.save_to_database(queries_mobile, city='almaty')
        logger.info("Saved mobile queries to database")
        
        logger.info("\nTesting pages collection...")
        # Test getting pages data
        pages = collector.get_pages(
            start_date=start_date,
            end_date=end_date,
            row_limit=100
        )
        logger.info(f"Got {len(pages)} pages")
        
        # Save pages data to database
        collector.save_to_database(pages, city='almaty')
        logger.info("Saved pages data to database")
        
        logger.info("\nTesting position metrics...")
        # Test getting position metrics for specific URL
        positions = collector.get_position_metrics(
            start_date=start_date,
            end_date=end_date,
            url="https://cvety.kz/"  # Замените на ваш URL
        )
        logger.info(f"Got position metrics for homepage: {len(positions)} entries")
        
        # Save position metrics to database
        collector.save_to_database(positions, city='almaty')
        logger.info("Saved position metrics to database")
        
        logger.info("\nTesting database retrieval...")
        # Test getting metrics from database
        stored_metrics = collector.get_metrics_for_period(
            start_date=start_date,
            end_date=end_date,
            city='almaty'
        )
        logger.info(f"Retrieved {len(stored_metrics)} metrics from database")
        
        # Print sample of retrieved data
        if stored_metrics:
            sample = stored_metrics[0]
            logger.info("\nSample metric from database:")
            logger.info(f"Date: {sample['date']}")
            logger.info(f"Query: {sample['query']}")
            logger.info(f"Clicks: {sample['clicks']}")
            logger.info(f"Position: {sample['position']}")
            logger.info(f"CTR: {sample['ctr']}")
        
        logger.info("\nAll tests completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        return False

if __name__ == "__main__":
    test_gsc_collector()
