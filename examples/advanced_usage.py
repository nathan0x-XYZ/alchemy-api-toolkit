#!/usr/bin/env python3
# Advanced usage example for Alchemy API Toolkit
# This example demonstrates more advanced features of the toolkit

import os
import sys
import logging
import asyncio
import time
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import toolkit modules
from validate_api_key import is_valid_alchemy_key
from alchemy_api_debug import handle_alchemy_error, batch_get_eth_balances
from retry_with_backoff import retry_with_backoff
from rate_limiter import RateLimiter
from fetch_nft_examples import get_nfts_for_owner, get_nft_transfers, resolve_ipfs_uri
from test_network_connection import test_alchemy_connection

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("alchemy_advanced.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("alchemy_advanced")

# Load environment variables
load_dotenv()
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")

# Create a rate limiter (300 calls per minute)
rate_limiter = RateLimiter(max_calls=300, time_frame=60)

# Create a custom retry function with our rate limiter
@retry_with_backoff(max_retries=5, backoff_factor=2)
def rate_limited_api_call(func, *args, **kwargs):
    """Make an API call with rate limiting and retry logic"""
    # Wait if we're exceeding rate limits
    rate_limiter.wait_if_needed()
    
    # Make the actual API call
    return func(*args, **kwargs)

async def main():
    """Main function demonstrating advanced toolkit usage"""
    
    # Check if API key exists
    if not ALCHEMY_API_KEY:
        logger.error("Alchemy API key not found. Please set ALCHEMY_API_KEY in .env file")
        return
    
    # Step 1: Test network connection
    logger.info("Testing connection to Alchemy API...")
    connection_status = test_alchemy_connection()
    if not connection_status.get('success'):
        logger.error(f"Connection test failed: {connection_status.get('error')}")
        return
    
    logger.info(f"Connection successful. Latency: {connection_status.get('latency')}ms")
    
    # Step 2: Batch get ETH balances
    try:
        addresses = [
            "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
            "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
            "0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8"
        ]
        logger.info(f"Getting ETH balances for {len(addresses)} addresses...")
        balances = batch_get_eth_balances(addresses)
        
        for address, balance in balances.items():
            logger.info(f"Address: {address}, Balance: {balance} ETH")
    except Exception as e:
        logger.error(f"Error getting batch ETH balances: {str(e)}")
    
    # Step 3: Get NFT transfers with rate limiting
    try:
        address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
        logger.info(f"Getting NFT transfers for {address}...")
        
        # Use our rate-limited function
        transfers = rate_limited_api_call(
            get_nft_transfers,
            address,
            page_size=10,
            max_pages=2
        )
        
        logger.info(f"Found {len(transfers.get('transfers', []))} NFT transfers")
        
        # Process some transfers
        for transfer in transfers.get('transfers', [])[:3]:
            logger.info(f"Transfer: {transfer.get('hash')} - {transfer.get('asset')}")
            
            # If there's an IPFS URI, resolve it
            if 'ipfs://' in str(transfer.get('metadata', '')):
                ipfs_uri = transfer.get('metadata')
                logger.info(f"Resolving IPFS URI: {ipfs_uri}")
                metadata = resolve_ipfs_uri(ipfs_uri)
                logger.info(f"Resolved metadata: {metadata}")
    except Exception as e:
        logger.error(f"Error working with NFT transfers: {str(e)}")
    
    logger.info("Advanced example completed successfully")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
