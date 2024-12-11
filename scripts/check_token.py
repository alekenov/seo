"""Check token format."""

import os
import json
import logging
from google.oauth2.credentials import Credentials
from src.utils.token_manager import TokenManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_token():
    """Check token format."""
    try:
        # Load token
        token_manager = TokenManager()
        token_data = token_manager.load_token('gsc')
        
        logger.info("Token data:")
        logger.info(json.dumps(token_data, indent=2))
        
        # Convert to Credentials object
        creds = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')
        )
        
        logger.info("\nCredentials info:")
        logger.info(f"Valid: {creds.valid}")
        logger.info(f"Expired: {creds.expired}")
        logger.info(f"Has refresh token: {creds.refresh_token is not None}")
        logger.info(f"Scopes: {creds.scopes}")
        
    except Exception as e:
        logger.error(f"Error checking token: {e}")
        raise

if __name__ == "__main__":
    check_token()
