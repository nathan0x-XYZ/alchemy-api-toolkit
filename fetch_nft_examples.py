import os
import time
import logging
import requests
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

# Validate API key exists
if not ALCHEMY_API_KEY:
    logger.error("[ERROR] ALCHEMY_API_KEY environment variable not found! Please ensure it exists in your .env file.")
    exit(1)

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
                
            logger.info(f"Fetching NFT page {page_count}" + (f" (pageKey: {next_page_key[:10]}...)" if next_page_key else ""))
            
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
                status_code = e.response.status_code
                
                if status_code == 400:
                    try:
                        error_detail = e.response.json()
                        logger.error(f"[ERROR] Request error (400): {error_detail}")
                    except:
                        logger.error(f"[ERROR] Request error (400): {e}")
                    break
                    
                elif status_code == 429:
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
                try:
                    error_detail = e.response.json()
                    logger.error(f"[ERROR] Failed to get metadata (400): {error_detail}")
                except:
                    logger.error(f"[ERROR] Failed to get metadata (400): {e}")
                
                # 400 errors usually indicate bad request format, don't retry
                return {
                    "success": False,
                    "error": "bad_request",
                    "message": str(e),
                    "contract_address": contract_address,
                    "token_id": token_id
                }
                
            elif status_code == 404:
                logger.warning(f"[WARNING] NFT not found: {contract_address}/{token_id}")
                return {
                    "success": False,
                    "error": "not_found",
                    "message": "NFT does not exist or metadata is unavailable",
                    "contract_address": contract_address,
                    "token_id": token_id
                }
                
            elif status_code == 429:
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
                logger.error(f"[ERROR] HTTP error: {e}")
                attempts += 1
                last_error = e
                
                if attempts < retry_count:
                    wait_time = retry_delay * (2 ** (attempts - 1))
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
        
        except requests.exceptions.Timeout:
            logger.warning(f"[WARNING] Request timeout")
            attempts += 1
            last_error = "Timeout"
            
            if attempts < retry_count:
                wait_time = retry_delay * (2 ** (attempts - 1))
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
                
        except Exception as e:
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

# Example usage
def nft_demo():
    """Demo of NFT API usage with error handling"""
    # Example: Get NFTs for a known address
    owner_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Vitalik's address
    print(f"\n=== Getting NFTs for {owner_address} ===")
    result = get_nfts_for_owner(owner_address, page_size=5, max_pages=1)
    
    if result["success"]:
        print(f"Successfully retrieved {result['total']} NFTs")
        
        # If we have NFTs, get metadata for the first one
        if result["nfts"]:
            nft = result["nfts"][0]
            contract_address = nft.get("contract", {}).get("address")
            token_id = nft.get("id", {}).get("tokenId")
            
            if contract_address and token_id:
                print(f"\n=== Getting metadata for NFT {contract_address}/{token_id} ===")
                metadata_result = get_nft_metadata(contract_address, token_id)
                
                if metadata_result["success"]:
                    print("Successfully retrieved NFT metadata")
                    
                    # Check if there's an IPFS URI to resolve
                    token_uri = metadata_result["metadata"].get("tokenUri", {}).get("raw")
                    if token_uri and token_uri.startswith("ipfs://"):
                        print(f"\n=== Resolving IPFS URI: {token_uri} ===")
                        ipfs_result = resolve_ipfs_uri(token_uri)
                        
                        if ipfs_result:
                            print("Successfully resolved IPFS URI")
                        else:
                            print("Failed to resolve IPFS URI")
                else:
                    print(f"Failed to get NFT metadata: {metadata_result.get('error')}")
    else:
        print(f"Failed to get NFTs: {result.get('error')}")

if __name__ == "__main__":
    nft_demo()
