"""Token management utilities."""
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from google.oauth2.credentials import Credentials
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TokenManager:
    """Manages OAuth tokens for various services."""
    
    def __init__(self, token_dir: str = None):
        """Initialize token manager.
        
        Args:
            token_dir: Directory to store token files. Defaults to ~/.seobot/tokens/
        """
        if token_dir is None:
            home = os.path.expanduser("~")
            token_dir = os.path.join(home, ".seobot", "tokens")
        
        self.token_dir = token_dir
        os.makedirs(token_dir, exist_ok=True)
    
    def _get_token_path(self, service: str) -> str:
        """Get path to token file for specific service.
        
        Args:
            service: Service name (e.g., 'gsc' for Google Search Console)
            
        Returns:
            Path to token file
        """
        return os.path.join(self.token_dir, f"{service}_token.json")
    
    def save_token(self, service: str, credentials: Credentials) -> bool:
        """Save token to file.
        
        Args:
            service: Service name
            credentials: OAuth credentials
            
        Returns:
            True if successful, False otherwise
        """
        try:
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            
            token_path = self._get_token_path(service)
            with open(token_path, 'w') as f:
                json.dump(token_data, f)
            
            logger.info(f"Token saved for service: {service}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving token for {service}: {str(e)}")
            return False
    
    def load_token(self, service: str) -> Optional[Dict[str, Any]]:
        """Load token from file.
        
        Args:
            service: Service name
            
        Returns:
            Token data if found and valid, None otherwise
        """
        try:
            token_path = self._get_token_path(service)
            if not os.path.exists(token_path):
                return None
            
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            
            # Check if token is expired
            if token_data.get('expiry'):
                expiry = datetime.fromisoformat(token_data['expiry'])
                if expiry <= datetime.utcnow():
                    logger.warning(f"Token for {service} is expired")
                    return None
            
            logger.info(f"Token loaded for service: {service}")
            return token_data
            
        except Exception as e:
            logger.error(f"Error loading token for {service}: {str(e)}")
            return None
    
    def create_credentials(self, token_data: Dict[str, Any]) -> Optional[Credentials]:
        """Create Credentials object from token data.
        
        Args:
            token_data: Token data dictionary
            
        Returns:
            Credentials object if successful, None otherwise
        """
        try:
            expiry = (datetime.fromisoformat(token_data['expiry']) 
                     if token_data.get('expiry') else None)
            
            credentials = Credentials(
                token=token_data['token'],
                refresh_token=token_data['refresh_token'],
                token_uri=token_data['token_uri'],
                client_id=token_data['client_id'],
                client_secret=token_data['client_secret'],
                scopes=token_data['scopes'],
                expiry=expiry
            )
            
            return credentials
            
        except Exception as e:
            logger.error(f"Error creating credentials: {str(e)}")
            return None
