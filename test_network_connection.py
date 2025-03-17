# File: test_network_connection.py
# Purpose: Add network connectivity test utility for Alchemy API endpoints

import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")

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

def test_alchemy_connection():
    """
    Tests the connection to Alchemy API endpoints
    
    Returns:
        dict: A dictionary containing connection status, latency, and error if any
    """
    try:
        # Ethereum mainnet endpoint
        network = "eth-mainnet"
        url = f"https://{network}.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
        
        # Simple request to get the latest block number
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }
        
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=5)
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                return {
                    "success": True,
                    "latency": round(latency, 2),
                    "block_number": int(result["result"], 16)
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {result.get('error', {}).get('message', 'Unknown error')}"
                }
        else:
            return {
                "success": False,
                "error": f"HTTP error: {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Test basic network connection
    result = test_network_connection()
    print(f"Basic connection test result: {'Success' if result else 'Failed'}")
    
    # Test Alchemy API connection
    alchemy_result = test_alchemy_connection()
    if alchemy_result["success"]:
        print(f"Alchemy API connection successful!")
        print(f"Latency: {alchemy_result['latency']}ms")
        print(f"Current block: {alchemy_result['block_number']}")
    else:
        print(f"Alchemy API connection failed: {alchemy_result['error']}")
