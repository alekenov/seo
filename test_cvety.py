"""Test script for cvety.kz Search Console data."""
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def test_cvety_metrics():
    """Test getting metrics for cvety.kz."""
    try:
        # Define the required scopes
        SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
        SITE_URL = 'sc-domain:cvety.kz'  # Using domain property
        
        # Initialize the OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'config/credentials.json', SCOPES)
        
        # Run the OAuth2 flow
        credentials = flow.run_local_server(port=0)
        
        # Build the service
        service = build('searchconsole', 'v1', credentials=credentials)
        
        # Get date range (last 7 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        # Request body for getting search analytics data
        request = {
            'startDate': start_date.isoformat(),
            'endDate': end_date.isoformat(),
            'dimensions': ['query', 'page'],
            'rowLimit': 10,  # Get top 10 results
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'country',
                    'expression': 'kaz'  # Filter for Kazakhstan
                }]
            }]
        }
        
        # Execute request
        response = service.searchanalytics().query(
            siteUrl=SITE_URL, 
            body=request
        ).execute()
        
        print(f"\nSuccessfully connected to {SITE_URL}")
        print("\nTop 10 queries for the last 7 days:")
        print("-" * 50)
        
        if 'rows' in response:
            for row in response['rows']:
                print(f"\nQuery: {row['keys'][0]}")
                print(f"Page: {row['keys'][1]}")
                print(f"Clicks: {row['clicks']}")
                print(f"Impressions: {row['impressions']}")
                print(f"CTR: {row['ctr']:.2%}")
                print(f"Position: {row['position']:.1f}")
        else:
            print("No data found for the specified period")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_cvety_metrics()
