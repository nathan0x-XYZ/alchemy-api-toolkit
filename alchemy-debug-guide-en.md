<!-- File: alchemy-debug-guide-en.md -->
<!-- Purpose: Add comprehensive debugging guide for Alchemy API (English version) -->

# Alchemy API Debug Guide

![Alchemy Logo](https://www.alchemy.com/images/alchemylogo.svg)

> A comprehensive guide for debugging and troubleshooting Alchemy API integration issues.

## Table of Contents
- [Common Error Codes and Solutions](#common-error-codes-and-solutions)
- [API Connection Troubleshooting](#api-connection-troubleshooting)
- [How to Avoid API Rate Limits](#how-to-avoid-api-rate-limits)
- [Best Practices for Error Handling](#best-practices-for-error-handling)
- [Python Examples: Capturing and Handling API Errors](#python-examples-capturing-and-handling-api-errors)
- [NFT API Examples](#nft-api-examples)

## Common Error Codes and Solutions

### 403 Forbidden
**Causes**:
- Invalid or expired API key
- Insufficient API key permissions
- Blocked IP address
- Subscription plan limitations

**Solutions**:
1. **Verify API Key**: Confirm that your API key is correct and hasn't expired
   ```python
   # Check API key format
   import re
   def is_valid_alchemy_key(api_key):
       pattern = r'^[a-zA-Z0-9_-]{32,}$'
       return bool(re.match(pattern, api_key))
   ```

2. **Check Plan Limitations**: Verify that your subscription plan supports the API features you're trying to access
3. **Contact Alchemy Support**: If you've confirmed your API key is correct but still encounter 403 errors, contact Alchemy support

### 429 Too Many Requests
**Causes**:
- Exceeding API rate limits
- Sending too many requests in a short time
- Not implementing proper backoff strategies

**Solutions**:
1. **Implement Exponential Backoff**: Use exponential backoff retry strategy when encountering 429 errors
2. **Batch Requests**: Combine multiple individual requests into batch requests
3. **Use Caching**: Cache frequently used data to reduce API calls
4. **Monitor Usage**: Regularly monitor your API usage to avoid hitting limits

### 500 Internal Server Error
**Causes**:
- Alchemy server issues
- Network connectivity problems
- Incorrect request format

**Solutions**:
1. **Retry Requests**: Automatically retry requests using backoff strategies
2. **Check Request Format**: Ensure your request format is correct, especially JSON-RPC parameters
3. **Contact Support**: If the problem persists, contact Alchemy support and provide detailed error information

## API Connection Troubleshooting

### Connection Timeout Issues
Connection timeouts are typically caused by network problems or high server load on Alchemy's end.

**Troubleshooting Steps**:
1. **Test Network Connection**
   ```python
   import requests
   import time
   
   def test_network_connection():
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
   ```

2. **Check Alchemy Status Page**
   Verify if there are any known outages or maintenance on Alchemy services
   Visit: https://status.alchemy.com

3. **Try Different Node URLs**
   If you're using a specific network (like Ethereum Mainnet), try nodes for other networks

### Connection Refused Issues
If API connections are being refused, this could be due to firewall settings or IP restrictions.

**Troubleshooting Steps**:
1. **Check IP Whitelist**: Confirm that your IP address has been added to the whitelist in your Alchemy dashboard
2. **Check VPN/Proxy**: If using a VPN or proxy, try disabling them
3. **Check Firewall Settings**: Ensure your firewall isn't blocking connections to the Alchemy API

## How to Avoid API Rate Limits

### Implement a Rate Limit Tracker
```python
import time
import threading

class RateLimiter:
    def __init__(self, max_calls, time_frame):
        self.max_calls = max_calls  # Maximum number of calls allowed within the time frame
        self.time_frame = time_frame  # Time frame in seconds
        self.calls = []  # Record of call timestamps
        self.lock = threading.Lock()
        
    def can_call(self):
        """Check if an API call can be made"""
        with self.lock:
            now = time.time()
            # Remove call records outside the time frame
            self.calls = [t for t in self.calls if now - t < self.time_frame]
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False
    
    def wait_time(self):
        """Return the time to wait (in seconds)"""
        with self.lock:
            if len(self.calls) < self.max_calls:
                return 0
            
            now = time.time()
            oldest_call = min(self.calls)
            return max(0, self.time_frame - (now - oldest_call))
```

### Best Practices
1. **Use Batch Queries**: Combine multiple requests to reduce API calls
   ```python
   # Querying multiple address balances individually
   # Not recommended
   balances = []
   for address in addresses:
       balance = web3.eth.get_balance(address)
       balances.append(balance)
   
   # Using batch queries
   # Recommended
   batch_payload = [
       {"jsonrpc": "2.0", "id": i, "method": "eth_getBalance", "params": [addr, "latest"]} 
       for i, addr in enumerate(addresses)
   ]
   response = requests.post(ALCHEMY_URL, json=batch_payload)
   batch_results = response.json()
   ```

2. **Implement Caching Mechanisms**: Cache frequently used data to reduce request volume
   ```python
   import functools

   @functools.lru_cache(maxsize=128)
   def get_transaction(tx_hash):
       """Get transaction details (with caching)"""
       return web3.eth.get_transaction(tx_hash)
   ```

3. **Use Webhooks Instead of Polling**: Set up Alchemy Webhooks to receive event notifications instead of frequent polling

4. **Implement Backoff Strategies**: Increase request intervals when approaching rate limits

## Best Practices for Error Handling

### Implement Retry Mechanisms

Use exponential backoff retry strategy to handle temporary errors:

```python
import time
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
    """Handle Alchemy API errors and provide useful debugging information"""
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
    """Get ETH balance with error handling and retry mechanism"""
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
                jitter = delay * 0.1 * (2 * (0.5 - 0.5))  # Add jitter in ±10% range
                sleep_time = delay + jitter
                
                logger.info(f"Backing off for {sleep_time:.2f} seconds, retry {retries}/{max_retries}")
                time.sleep(sleep_time)
            else:
                # For errors that don't need backoff, retry immediately
                logger.info(f"Retrying immediately {retries}/{max_retries}")

def batch_get_eth_balances(addresses):
    """Batch get ETH balances for multiple addresses"""
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

## NFT API Examples

Alchemy provides powerful NFT APIs for retrieving NFT data, metadata, and ownership information. The following examples demonstrate how to use these APIs with proper error handling and best practices.

### Retrieving NFTs Owned by an Address

The following example shows how to retrieve all NFTs owned by an address with pagination handling, error handling, and rate limit avoidance:

```python
def get_nfts_for_owner(owner_address, page_size=100, max_pages=None, include_spam=False):
    """
    Get all NFTs owned by an address, handling pagination and errors
    
    Args:
        owner_address (str): The Ethereum address to query
        page_size (int): Number of NFTs to fetch per page
        max_pages (int): Maximum number of pages to fetch (None for all)
        include_spam (bool): Whether to include spam NFTs
        
    Returns:
        dict: Result containing NFTs and status information
    """
    
    url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{ALCHEMY_API_KEY}/getNFTs"
    params = {
        "owner": owner_address,
        "pageSize": page_size,
        "withMetadata": "true",
        "excludeFilters": [] if include_spam else ["SPAM"]
    }
    
    all_nfts = []
    page_count = 0
    next_page_key = None
    
    try:
        while True:
            page_count += 1
            
            # Add pagination parameter (if exists)
            if next_page_key:
                params["pageKey"] = next_page_key
                
            logger.info(f"Fetching NFT page {page_count}" + 
                       (f" (pageKey: {next_page_key[:10]}...)" if next_page_key else ""))
            
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # Get NFTs from this page
                nfts = data.get("ownedNfts", [])
                all_nfts.extend(nfts)
                
                logger.info(f"Retrieved {len(nfts)} NFTs, total {len(all_nfts)}")
                
                # Check if there's another page
                next_page_key = data.get("pageKey")
                if not next_page_key:
                    logger.info(f"[SUCCESS] Retrieved all NFTs, total {len(all_nfts)}")
                    break
                
                # Check if we've reached the max page limit
                if max_pages and page_count >= max_pages:
                    logger.warning(f"[WARNING] Reached max page limit ({max_pages}), retrieved {len(all_nfts)} NFTs")
                    break
                
                # Add small delay to avoid rate limits
                time.sleep(0.5)
                
            except requests.exceptions.HTTPError as e:
                # Handle HTTP errors with specific status codes
                status_code = e.response.status_code
                
                if status_code == 400:
                    # Handle bad request errors
                    try:
                        error_detail = e.response.json()
                        logger.error(f"[ERROR] Request error (400): {error_detail}")
                    except:
                        logger.error(f"[ERROR] Request error (400): {e}")
                    break
                    
                elif status_code == 429:
                    # Handle rate limit errors with backoff
                    logger.warning(f"[WARNING] Rate limit reached (429), waiting 2 seconds...")
                    time.sleep(2)
                    continue
                    
                else:
                    logger.error(f"[ERROR] HTTP error: {e}")
                    break
            
            except requests.exceptions.Timeout:
                logger.warning(f"[WARNING] Request timeout, retrying...")
                continue
                
            except Exception as e:
                logger.error(f"[ERROR] Error retrieving NFTs: {e}")
                break
        
        return {
            "success": True,
            "nfts": all_nfts,
            "total": len(all_nfts),
            "owner": owner_address,
            "pages_fetched": page_count
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error during NFT retrieval: {e}")
        return {
            "success": False,
            "error": "unexpected_error",
            "message": str(e),
            "nfts": all_nfts,
            "total": len(all_nfts),
            "owner": owner_address,
            "pages_fetched": page_count
        }
```

### Retrieving NFT Metadata with Retry Logic

This example demonstrates how to retrieve NFT metadata with a robust retry mechanism and exponential backoff:

```python
def get_nft_metadata(contract_address, token_id, retry_count=3, retry_delay=1):
    """
    Get NFT metadata with error handling and retry mechanism
    
    Args:
        contract_address (str): The NFT contract address
        token_id (str): The NFT token ID
        retry_count (int): Number of retry attempts
        retry_delay (int): Initial delay between retries in seconds
        
    Returns:
        dict: Result containing metadata and status information
    """
    
    url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{ALCHEMY_API_KEY}/getNFTMetadata"
    params = {
        "contractAddress": contract_address,
        "tokenId": token_id,
        "refreshCache": "false"
    }
    
    attempts = 0
    last_error = None
    
    while attempts < retry_count:
        try:
            logger.info(f"Fetching NFT metadata: {contract_address}/{token_id} (attempt {attempts+1}/{retry_count})")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            metadata = response.json()
            logger.info(f"[SUCCESS] Successfully retrieved metadata for NFT {contract_address}/{token_id}")
            
            # Check if metadata is complete
            if not metadata.get('metadata'):
                logger.warning(f"[WARNING] NFT metadata may be incomplete, missing 'metadata' field")
            
            return {
                "success": True,
                "metadata": metadata,
                "contract_address": contract_address,
                "token_id": token_id
            }
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            
            if status_code == 400:
                # Handle bad request errors (don't retry)
                try:
                    error_detail = e.response.json()
                    logger.error(f"[ERROR] Failed to get metadata (400): {error_detail}")
                except:
                    logger.error(f"[ERROR] Failed to get metadata (400): {e}")
                
                return {
                    "success": False,
                    "error": "bad_request",
                    "message": str(e),
                    "contract_address": contract_address,
                    "token_id": token_id
                }
                
            elif status_code == 404:
                # Handle not found errors (don't retry)
                logger.warning(f"[WARNING] NFT not found: {contract_address}/{token_id}")
                return {
                    "success": False,
                    "error": "not_found",
                    "message": "NFT does not exist or metadata is unavailable",
                    "contract_address": contract_address,
                    "token_id": token_id
                }
                
            elif status_code == 429:
                # Handle rate limit errors with exponential backoff
                logger.warning(f"[WARNING] NFT API rate limit reached (429): {e}")
                attempts += 1
                last_error = e
                
                if attempts < retry_count:
                    wait_time = retry_delay * (2 ** (attempts - 1))  # Exponential backoff
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                    
                return {
                    "success": False,
                    "error": "rate_limit",
                    "message": "API rate limit reached, all retries failed",
                    "contract_address": contract_address,
                    "token_id": token_id
                }
                
            else:
                # Handle other HTTP errors with retry
                logger.error(f"[ERROR] HTTP error: {e}")
                attempts += 1
                last_error = e
                
                if attempts < retry_count:
                    wait_time = retry_delay * (2 ** (attempts - 1))
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
        
        except requests.exceptions.Timeout:
            # Handle timeout errors with retry
            logger.warning(f"[WARNING] Request timeout")
            attempts += 1
            last_error = "Timeout"
            
            if attempts < retry_count:
                wait_time = retry_delay * (2 ** (attempts - 1))
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
                
        except Exception as e:
            # Handle other exceptions with retry
            logger.error(f"[ERROR] Error retrieving NFT metadata: {e}")
            attempts += 1
            last_error = e
            
            if attempts < retry_count:
                wait_time = retry_delay * (2 ** (attempts - 1))
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
    
    # If all retries failed
    logger.error(f"[ERROR] Failed to get NFT metadata after {retry_count} attempts")
    return {
        "success": False,
        "error": "all_retries_failed",
        "message": f"All retries failed: {last_error}",
        "contract_address": contract_address,
        "token_id": token_id
    }
```

### Resolving IPFS URIs for NFT Metadata

NFT metadata often contains IPFS URIs that need to be resolved. This example shows how to handle IPFS resolution with fallback gateways:

```python
def resolve_ipfs_uri(ipfs_uri, timeout=15):
    """
    Resolve IPFS URI to get metadata
    
    Args:
        ipfs_uri (str): IPFS URI to resolve
        timeout (int): Request timeout in seconds
        
    Returns:
        dict or bytes: Resolved content (JSON or binary)
    """
    if not ipfs_uri:
        logger.error("[ERROR] IPFS URI is empty")
        return None
        
    try:
        # Convert IPFS URI to HTTP gateway URL
        if ipfs_uri.startswith("ipfs://"):
            http_uri = ipfs_uri.replace("ipfs://", "https://ipfs.io/ipfs/")
        elif ipfs_uri.startswith("ipfs:/"):
            http_uri = ipfs_uri.replace("ipfs:/", "https://ipfs.io/ipfs/")
        else:
            http_uri = ipfs_uri
            
        logger.info(f"Resolving IPFS URI: {ipfs_uri} -> {http_uri}")
        
        # Get metadata with timeout
        response = requests.get(http_uri, timeout=timeout)
        response.raise_for_status()
        
        if "content-type" in response.headers and "application/json" in response.headers["content-type"]:
            logger.info("[SUCCESS] Successfully retrieved JSON metadata from IPFS")
            return response.json()
        else:
            logger.info("[SUCCESS] Retrieved non-JSON content from IPFS")
            return response.content
            
    except requests.exceptions.Timeout:
        logger.warning(f"[WARNING] IPFS gateway timeout: {ipfs_uri}")
        
        # Try alternate gateway
        try:
            alt_gateway = ipfs_uri.replace("ipfs://", "https://cloudflare-ipfs.com/ipfs/")
            logger.info(f"Trying alternate gateway: {alt_gateway}")
            
            alt_response = requests.get(alt_gateway, timeout=timeout)
            alt_response.raise_for_status()
            
            if "content-type" in alt_response.headers and "application/json" in alt_response.headers["content-type"]:
                logger.info("[SUCCESS] Successfully retrieved JSON metadata from alternate IPFS gateway")
                return alt_response.json()
            else:
                logger.info("[SUCCESS] Retrieved non-JSON content from alternate IPFS gateway")
                return alt_response.content
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to resolve IPFS URI with alternate gateway: {e}")
            return None
            
    except Exception as e:
        logger.error(f"[ERROR] Failed to resolve IPFS URI: {e}")
        return None
```

### Best Practices for NFT API Usage

1. **Implement Pagination Handling**: NFT collections can be large, so always implement proper pagination handling.
2. **Use Exponential Backoff**: When encountering rate limits, implement exponential backoff with jitter.
3. **Handle IPFS Resolution Failures**: IPFS gateways can be unreliable, so implement fallback gateways.
4. **Cache NFT Metadata**: NFT metadata rarely changes, so cache it to reduce API calls.
5. **Filter Spam NFTs**: Use the `excludeFilters` parameter to filter out spam NFTs.
6. **Implement Robust Error Handling**: Handle all possible error cases, including network errors, timeouts, and API errors.

## Python Examples: Capturing and Handling API Errors

### Complete Alchemy API Error Handling Example

```python
import os
import time
import requests
import logging
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
    """Handle Alchemy API errors and provide useful debugging information"""
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
    """Get ETH balance with error handling and retry mechanism"""
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
                jitter = delay * 0.1 * (2 * (0.5 - 0.5))  # Add jitter in ±10% range
                sleep_time = delay + jitter
                
                logger.info(f"Backing off for {sleep_time:.2f} seconds, retry {retries}/{max_retries}")
                time.sleep(sleep_time)
            else:
                # For errors that don't need backoff, retry immediately
                logger.info(f"Retrying immediately {retries}/{max_retries}")

def batch_get_eth_balances(addresses):
    """Batch get ETH balances for multiple addresses"""
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

### How to Use

1. Create a `.env` file and add your Alchemy API key:
   ```
   ALCHEMY_API_KEY=your_alchemy_api_key
   ```

2. Install the required dependencies:
   ```bash
   pip install web3 requests python-dotenv
   ```

3. Run the example:
   ```bash
   python alchemy_api_debug.py
   ```

## Additional Resources

- [Alchemy Documentation](https://docs.alchemy.com/)
- [Alchemy Dashboard](https://dashboard.alchemy.com/)
- [Alchemy Discord Community](https://discord.gg/alchemyplatform)
- [Web3.py Documentation](https://web3py.readthedocs.io/)

---

*Last Updated: March 2025*
