#!/usr/bin/env python3
# Batch processing example for Alchemy API Toolkit
# This example demonstrates how to process large amounts of data efficiently

import os
import sys
import logging
import time
import concurrent.futures
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import toolkit modules
from validate_api_key import is_valid_alchemy_key
from alchemy_api_debug import batch_get_eth_balances
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

def process_nft_batch(address_batch):
    """Process a batch of addresses to get their NFTs"""
    results = {}
    
    for address in address_batch:
        # Wait if we're exceeding rate limits
        rate_limiter.wait_if_needed()
        
        logger.info(f"Getting NFTs for {address}...")
        try:
            nfts = get_nfts_for_owner(address, page_size=10, max_pages=1)
            results[address] = {
                'count': len(nfts.get('nfts', [])),
                'nfts': nfts.get('nfts', [])
            }
            logger.info(f"Found {results[address]['count']} NFTs for {address}")
        except Exception as e:
            logger.error(f"Error getting NFTs for {address}: {str(e)}")
            results[address] = {'error': str(e)}
    
    return results

def main():
    """Main function demonstrating batch processing"""
    
    # Step 1: Validate API key
    if not is_valid_alchemy_key(ALCHEMY_API_KEY):
        logger.error("Invalid Alchemy API key format")
        return
    
    # Step 2: Define a list of addresses to process
    addresses = [
        "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
        "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
        "0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8",
        "0x1Db3439a222C519ab44bb1144fC28167b4Fa6EE6",
        "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    ]
    
    # Step 3: Get ETH balances in batch
    logger.info(f"Getting ETH balances for {len(addresses)} addresses...")
    try:
        balances = batch_get_eth_balances(addresses)
        for address, balance in balances.items():
            logger.info(f"Address: {address}, Balance: {balance} ETH")
    except Exception as e:
        logger.error(f"Error getting batch ETH balances: {str(e)}")
    
    # Step 4: Process NFTs in parallel batches
    logger.info("Processing NFTs in parallel batches...")
    
    # Split addresses into batches of 2
    batch_size = 2
    address_batches = [addresses[i:i+batch_size] for i in range(0, len(addresses), batch_size)]
    
    # Process batches in parallel
    start_time = time.time()
    all_results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Submit batch processing tasks
        future_to_batch = {
            executor.submit(process_nft_batch, batch): i 
            for i, batch in enumerate(address_batches)
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_batch):
            batch_index = future_to_batch[future]
            try:
                batch_results = future.result()
                all_results.update(batch_results)
                logger.info(f"Completed batch {batch_index+1}/{len(address_batches)}")
            except Exception as e:
                logger.error(f"Batch {batch_index} generated an exception: {str(e)}")
    
    # Step 5: Summarize results
    end_time = time.time()
    logger.info(f"Batch processing completed in {end_time - start_time:.2f} seconds")
    
    total_nfts = sum(data.get('count', 0) for data in all_results.values() if 'count' in data)
    logger.info(f"Total NFTs found: {total_nfts}")
    
    # Step 6: Process some NFT metadata as an example
    for address, data in all_results.items():
        if 'nfts' in data and data['nfts']:
            # Get the first NFT for this address
            first_nft = data['nfts'][0]
            contract_address = first_nft.get('contract', {}).get('address')
            token_id = first_nft.get('id', {}).get('tokenId')
            
            if contract_address and token_id:
                logger.info(f"Getting metadata for NFT {contract_address}/{token_id}...")
                try:
                    # Wait if we're exceeding rate limits
                    rate_limiter.wait_if_needed()
                    
                    metadata = get_nft_metadata(contract_address, token_id)
                    nft_name = metadata.get('metadata', {}).get('name', 'Unknown')
                    logger.info(f"NFT {contract_address}/{token_id} name: {nft_name}")
                except Exception as e:
                    logger.error(f"Error getting NFT metadata: {str(e)}")
            
            # Only process one NFT as an example
            break
    
    logger.info("Batch processing example completed successfully")

if __name__ == "__main__":
    main()
