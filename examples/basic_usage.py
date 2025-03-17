#!/usr/bin/env python3
# Basic usage example for Alchemy API Toolkit
# This example demonstrates the core functionality of the toolkit

import os
import sys
import logging
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import toolkit modules
from validate_api_key import is_valid_alchemy_key
from alchemy_api_debug import handle_alchemy_error, get_eth_balance
from retry_with_backoff import retry_with_backoff
from fetch_nft_examples import get_nfts_for_owner, get_nft_metadata

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("alchemy_example.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("alchemy_example")

# Load environment variables
load_dotenv()
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")

def main():
    """Main function demonstrating toolkit usage"""
    
    # Step 1: Validate API key
    logger.info("Validating API key...")
    if not is_valid_alchemy_key(ALCHEMY_API_KEY):
        logger.error("Invalid Alchemy API key format")
        return
    
    logger.info("API key format is valid")
    
    # Step 2: Get ETH balance with error handling
    try:
        address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"  # Example address
        logger.info(f"Getting ETH balance for {address}...")
        balance = get_eth_balance(address)
        logger.info(f"ETH Balance: {balance} ETH")
    except Exception as e:
        logger.error(f"Error getting ETH balance: {str(e)}")
    
    # Step 3: Get NFTs for an address
    try:
        logger.info(f"Getting NFTs for {address}...")
        nfts = get_nfts_for_owner(address, page_size=5, max_pages=1)
        logger.info(f"Found {len(nfts.get('nfts', []))} NFTs")
        
        # If NFTs found, get metadata for the first one
        if nfts.get('nfts'):
            first_nft = nfts['nfts'][0]
            contract_address = first_nft.get('contract', {}).get('address')
            token_id = first_nft.get('id', {}).get('tokenId')
            
            if contract_address and token_id:
                logger.info(f"Getting metadata for NFT {contract_address}/{token_id}...")
                metadata = get_nft_metadata(contract_address, token_id)
                logger.info(f"NFT Metadata: {metadata.get('metadata', {}).get('name', 'Unknown')}")
    except Exception as e:
        logger.error(f"Error working with NFTs: {str(e)}")
    
    logger.info("Example completed successfully")

if __name__ == "__main__":
    main()
