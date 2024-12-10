"""Simple test script for Google Search Console API."""
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def test_gsc_connection():
    """Test connection to Google Search Console API."""
    try:
        # Define the required scopes
        SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
        
        # Initialize the OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'config/credentials.json', SCOPES)
        
        # Run the OAuth2 flow
        credentials = flow.run_local_server(port=0)
        
        # Build the service
        service = build('searchconsole', 'v1', credentials=credentials)
        
        # Try to list sites
        sites = service.sites().list().execute()
        
        print("Successfully connected to Google Search Console API")
        print(f"Found sites: {sites}")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_gsc_connection()
