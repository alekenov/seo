"""Check Google Search Console access."""

import os
import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from src.utils.token_manager import TokenManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_gsc_access():
    """Check access to Google Search Console."""
    try:
        # Load token
        token_manager = TokenManager()
        token_data = token_manager.load_token('gsc')
        
        if not token_data:
            logger.error("No credentials found. Please authenticate first.")
            return
            
        # Convert to Credentials object
        creds = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')
        )
            
        # Build service
        service = build('webmasters', 'v3', credentials=creds)
        
        # Get list of sites
        sites = service.sites().list().execute()
        
        logger.info("Sites you have access to:")
        for site in sites.get('siteEntry', []):
            logger.info(f"URL: {site['siteUrl']}")
            logger.info(f"Permission Level: {site.get('permissionLevel', 'unknown')}")
            logger.info(f"Owner: {site.get('owner', 'unknown')}")
            logger.info("-" * 50)
            
    except Exception as e:
        logger.error(f"Error checking GSC access: {e}")
        raise

if __name__ == "__main__":
    check_gsc_access()
