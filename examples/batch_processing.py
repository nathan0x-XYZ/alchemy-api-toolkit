#!/usr/bin/env python3
# Batch processing example for Alchemy API Toolkit
# This example demonstrates efficient processing of large datasets

import os
import sys
import logging
import asyncio
import time
import concurrent.futures
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import toolkit modules
from validate_api_key import is_valid_alchemy_key
from alchemy_api_debug import handle_alchemy_error, batch_get_eth_balances
from retry_with_backoff import retry_with_backoff
from rate_limiter import RateLimiter
from fetch_nft_examples import get_nfts_for_owner, get_nft_metadata

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("alchemy_batch.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("alchemy_batch")

# Load environment variables
load_dotenv()
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")

# Create a rate limiter (300 calls per minute)
rate_limiter = RateLimiter(max_calls=300, time_frame=60)

# List of addresses to process
ADDRESSES = [
    "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
    "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
    "0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8",
    "0x1Db3439a222C519ab44bb1144fC28167b4Fa6EE6",
    "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
]

async def process_nfts_for_address(address, batch_id):
    """Process NFTs for a single address with rate limiting"""
    try:
        # Wait if needed to respect rate limits
        rate_limiter.wait_if_needed()
        
        # Get NFTs for this address
        nfts = get_nfts_for_owner(address, page_size=10, max_pages=1)
        
        # Process the NFTs (in a real scenario, you might store them in a database)
        nft_count = len(nfts.get('nfts', []))
        logger.info(f"Batch {batch_id}: Found {nft_count} NFTs for {address}")
        
        return nft_count
    except Exception as e:
        logger.error(f"Batch {batch_id} generated an exception: {str(e)}")
        return 0

async def main():
    """Main function demonstrating batch processing"""
    
    # Check if API key exists
    if not ALCHEMY_API_KEY:
        logger.error("Alchemy API key not found. Please set ALCHEMY_API_KEY in .env file")
        return
        
    # Step 1: Validate API key
    if not is_valid_alchemy_key(ALCHEMY_API_KEY):
        logger.error("Invalid Alchemy API key format")
        return
    
    # Step 1: Get ETH balances in batch
    try:
        logger.info(f"Getting ETH balances for {len(ADDRESSES)} addresses...")
        balances = batch_get_eth_balances(ADDRESSES)
        
        for address, balance in balances.items():
            logger.info(f"Address: {address}, Balance: {balance} ETH")
    except Exception as e:
        logger.error(f"Error getting batch ETH balances: {str(e)}")
    
    # Step 2: Process NFTs in parallel batches
    logger.info("Processing NFTs in parallel batches...")
    start_time = time.time()
    
    # Create tasks for each address
    tasks = []
    for i, address in enumerate(ADDRESSES):
        # Divide addresses into batches
        batch_id = i % 3  # Create 3 batches
        tasks.append(process_nfts_for_address(address, batch_id))
    
    # Run tasks concurrently
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        total_nfts = sum([r for r in results if isinstance(r, int)])
        
        elapsed_time = time.time() - start_time
        logger.info(f"Batch processing completed in {elapsed_time:.2f} seconds")
        logger.info(f"Total NFTs found: {total_nfts}")
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
    
    logger.info("Batch processing example completed successfully")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
