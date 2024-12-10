"""Script to test Google Search Console API credentials."""
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

def test_credentials():
    """Test Google Search Console API credentials."""
    # Path to credentials file
    credentials_path = 'config/credentials.json'
    
    # Check if credentials file exists
    if not os.path.exists(credentials_path):
        logger.error(f"Credentials file not found at {credentials_path}")
        return False
    
    try:
        # Define the required scopes
        SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
        
        # Initialize the OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, SCOPES)
        
        # Run the OAuth2 flow
        credentials = flow.run_local_server(port=0)
        
        # Build the service
        service = build('searchconsole', 'v1', credentials=credentials)
        
        # Try to list sites
        sites = service.sites().list().execute()
        
        # Log success
        logger.info("Successfully connected to Google Search Console API")
        logger.info(f"Found {len(sites.get('siteEntry', []))} sites")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing credentials: {str(e)}")
        return False

if __name__ == '__main__':
    test_credentials()
