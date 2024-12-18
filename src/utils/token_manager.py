"""Token management utilities."""
import json
import psycopg2
from datetime import datetime
from typing import Optional, Dict, Any

from google.oauth2.credentials import Credentials
from src.config.config import config
from src.config.supabase_config import DATABASE_URL
from src.utils.credentials_manager import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TokenManager:
    """Manages OAuth tokens using PostgreSQL database."""
    
    def __init__(self):
        """Initialize token manager."""
        self.db_url = DATABASE_URL
        self.credentials_manager = CredentialsManager()
        self.gsc_credentials_file = config.GSC_CREDENTIALS_FILE
    
    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.db_url)
    
    def save_token(self, service: str, token_data: Dict[str, Any]) -> bool:
        """Save token to database.
        
        Args:
            service: Service name (e.g., 'gsc' for Google Search Console)
            token_data: Token data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Проверяем существование токена
                    cur.execute(
                        "SELECT id FROM tokens WHERE service = %s",
                        (service,)
                    )
                    result = cur.fetchone()
                    
                    # Если token_data уже строка JSON, используем как есть
                    token_json = token_data if isinstance(token_data, str) else json.dumps(token_data)
                    
                    if result:
                        # Обновляем существующий токен
                        cur.execute(
                            """
                            UPDATE tokens 
                            SET token_data = %s, updated_at = CURRENT_TIMESTAMP 
                            WHERE service = %s
                            """,
                            (token_json, service)
                        )
                    else:
                        # Создаем новый токен
                        cur.execute(
                            """
                            INSERT INTO tokens (service, token_data) 
                            VALUES (%s, %s)
                            """,
                            (service, token_json)
                        )
                    
                    conn.commit()
            
            logger.info(f"Token saved for service: {service}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving token for {service}: {str(e)}")
            return False
    
    def load_token(self, service: str) -> Optional[Dict[str, Any]]:
        """Load token from database.
        
        Args:
            service: Service name
            
        Returns:
            Token data if found and valid, None otherwise
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT token_data FROM tokens WHERE service = %s",
                        (service,)
                    )
                    result = cur.fetchone()
                    
                    if not result:
                        return None
                    
                    # Если token_data уже словарь, используем как есть
                    token_data = result[0]
                    if isinstance(token_data, str):
                        token_data = json.loads(token_data)
                    
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
        """Create Credentials object from token data and client credentials.
        
        Args:
            token_data: Token data dictionary
            
        Returns:
            Credentials object if successful, None otherwise
        """
        try:
            # Загружаем учетные данные клиента
            client_creds = self.credentials_manager.load_credentials('gsc')
            if not client_creds:
                logger.error("Client credentials not found")
                return None
            
            expiry = (datetime.fromisoformat(token_data['expiry']) 
                     if token_data.get('expiry') else None)
            
            credentials = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=client_creds.get('token_uri'),
                client_id=client_creds.get('client_id'),
                client_secret=client_creds.get('client_secret'),
                scopes=token_data.get('scopes'),
                expiry=expiry
            )
            
            return credentials
            
        except Exception as e:
            logger.error(f"Error creating credentials: {str(e)}")
            return None

    def setup_gsc_auth(self) -> Optional[Dict[str, Any]]:
        """Настройка аутентификации для Google Search Console.
        
        Returns:
            Данные токена если успешно, None в противном случае
        """
        try:
            # Проверяем существующий токен
            token_data = self.load_token('gsc')
            if token_data:
                creds = self.create_credentials(token_data)
                if creds and not creds.expired:
                    return token_data
            
            # Если токен не найден или истек, запускаем процесс аутентификации
            if not os.path.exists(self.gsc_credentials_file):
                logger.error(f"Credentials file not found: {self.gsc_credentials_file}")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.gsc_credentials_file,
                scopes=['https://www.googleapis.com/auth/webmasters.readonly']
            )
            
            creds = flow.run_local_server(port=0)
            token_data = json.loads(creds.to_json())
            
            # Сохраняем новый токен
            self.save_token('gsc', token_data)
            return token_data
            
        except Exception as e:
            logger.error(f"Error setting up GSC auth: {str(e)}")
            return None
