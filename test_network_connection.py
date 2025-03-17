# File: test_network_connection.py
# Purpose: Add network connectivity test utility for Alchemy API endpoints

import requests
import time

def test_network_connection():
    """
    Tests the network connection to Alchemy's health endpoint
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        start_time = time.time()
        response = requests.get('https://dashboard.alchemy.com/health', timeout=5)
        response_time = time.time() - start_time
        
        print(f"Network connection status: {response.status_code}")
        print(f"Response time: {response_time:.2f} seconds")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Network connection test failed: {e}")
        return False

if __name__ == "__main__":
    result = test_network_connection()
    print(f"Connection test result: {'Success' if result else 'Failed'}")
