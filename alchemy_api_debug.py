# File: alchemy_api_debug.py
# Purpose: Implement Alchemy API debugging tools with error handling and retry logic

import os
import time
import requests
import logging
import random
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError
from web3 import Web3
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("alchemy_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("alchemy_api")

# Load environment variables
load_dotenv()
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')
ALCHEMY_URL = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

def handle_alchemy_error(error, endpoint):
    """
    Handle Alchemy API errors and provide useful debugging information
    
    Args:
        error (Exception): The caught exception
        endpoint (str): The API endpoint that was called
        
    Returns:
        bool: True if backoff is needed, False otherwise
    """
    if isinstance(error, HTTPError):
        status_code = error.response.status_code
        if status_code == 403:
            logger.error(f"API authorization error (403): Check API key and permissions - {endpoint}")
            logger.debug(f"Response content: {error.response.text}")
        elif status_code == 429:
            logger.warning(f"Rate limit reached (429): Implement backoff strategy - {endpoint}")
            logger.debug(f"Response content: {error.response.text}")
            # Return signal to backoff
            return True
        elif status_code >= 500:
            logger.error(f"Alchemy server error ({status_code}): Retry later - {endpoint}")
            logger.debug(f"Response content: {error.response.text}")
            # Return signal to backoff
            return True
        else:
            logger.error(f"HTTP error ({status_code}): {error} - {endpoint}")
    elif isinstance(error, Timeout):
        logger.error(f"Request timeout: {error} - {endpoint}")
        return True
    elif isinstance(error, ConnectionError):
        logger.error(f"Connection error: {error} - {endpoint}")
        return True
    elif isinstance(error, RequestException):
        logger.error(f"Request exception: {error} - {endpoint}")
        return True
    else:
        logger.error(f"Unknown error: {error} - {endpoint}")
    
    return False

def get_eth_balance(address, max_retries=5):
    """
    Get ETH balance with error handling and retry mechanism
    
    Args:
        address (str): Ethereum address to check
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        float: ETH balance in ether units
        
    Raises:
        Exception: If all retries fail
    """
    endpoint = f"eth_getBalance - {address}"
    retries = 0
    base_delay = 1
    
    while retries <= max_retries:
        try:
            balance = w3.eth.get_balance(address)
            return Web3.from_wei(balance, 'ether')
            
        except Exception as e:
            # Handle error and check if backoff is needed
            need_backoff = handle_alchemy_error(e, endpoint)
            
            retries += 1
            if retries > max_retries:
                logger.error(f"Maximum retries reached ({max_retries}): {address}")
                raise
            
            if need_backoff:
                # Calculate backoff delay (with jitter)
                delay = min(30, base_delay * (2 ** (retries - 1)))
                jitter = random.uniform(0, 0.1 * delay)
                sleep_time = delay + jitter
                
                logger.info(f"Backing off for {sleep_time:.2f} seconds, retry {retries}/{max_retries}")
                time.sleep(sleep_time)
            else:
                # For errors that don't need backoff, retry immediately
                logger.info(f"Retrying immediately {retries}/{max_retries}")

def batch_get_eth_balances(addresses):
    """
    Batch get ETH balances for multiple addresses
    
    Args:
        addresses (list): List of Ethereum addresses
        
    Returns:
        dict: Dictionary mapping addresses to balances
        
    Raises:
        Exception: If the request fails
    """
    try:
        # Prepare batch request
        batch_payload = [
            {
                "jsonrpc": "2.0", 
                "id": i, 
                "method": "eth_getBalance", 
                "params": [addr, "latest"]
            } 
            for i, addr in enumerate(addresses)
        ]
        
        # Send batch request
        response = requests.post(ALCHEMY_URL, json=batch_payload)
        response.raise_for_status()  # Check for HTTP errors
        results = response.json()
        
        # Process results
        balances = {}
        for i, addr in enumerate(addresses):
            result = next((r for r in results if r["id"] == i), None)
            if result and "result" in result:
                balances[addr] = Web3.from_wei(int(result["result"], 16), 'ether')
            else:
                logger.warning(f"Could not get balance for address {addr}")
                balances[addr] = None
        
        return balances
        
    except Exception as e:
        handle_alchemy_error(e, "batch_get_eth_balances")
        raise

def main():
    """Main function demonstrating API error handling"""
    try:
        # Example 1: Get single address balance
        address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Vitalik's address
        balance = get_eth_balance(address)
        logger.info(f"ETH balance for address {address}: {balance}")
        
        # Example 2: Batch get multiple address balances
        addresses = [
            "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # Vitalik
            "0x00000000219ab540356cBB839Cbe05303d7705Fa",  # ETH2 deposit contract
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"   # WETH contract
        ]
        balances = batch_get_eth_balances(addresses)
        for addr, bal in balances.items():
            logger.info(f"ETH balance for address {addr}: {bal}")
            
    except Exception as e:
        logger.error(f"Program execution error: {e}")

if __name__ == "__main__":
    main()
