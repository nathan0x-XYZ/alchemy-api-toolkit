import os
import sys
import time
import logging
import requests
from dotenv import load_dotenv

# 設置控制台編碼為 UTF-8 (解決 Windows 下的編碼問題)
sys.stdout.reconfigure(encoding='utf-8')

# 設置日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("alchemy_api.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("alchemy_api")

# 載入環境變數
load_dotenv()
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')

# 驗證 API 密鑰是否存在
if not ALCHEMY_API_KEY:
    logger.error("[ERROR] ALCHEMY_API_KEY 環境變數未找到！請確保它存在於你的 .env 文件中。")
    exit(1)

def get_nft_metadata(contract_address, token_id, retry_count=3, retry_delay=1):
    """獲取 NFT 元數據，包含錯誤處理和重試機制"""
    
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
            logger.info(f"正在獲取 NFT 元數據: {contract_address}/{token_id} (嘗試 {attempts+1}/{retry_count})")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            metadata = response.json()
            logger.info(f"[SUCCESS] 成功獲取 NFT {contract_address}/{token_id} 的元數據")
            
            # 檢查元數據是否完整
            if not metadata.get('metadata'):
                logger.warning(f"[WARNING] NFT 元數據可能不完整，缺少 'metadata' 欄位")
            
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
                    logger.error(f"[ERROR] 獲取元數據失敗 (400): {error_detail}")
                except:
                    logger.error(f"[ERROR] 獲取元數據失敗 (400): {e}")
                
                # 400 錯誤通常表示請求格式錯誤，不重試
                return {
                    "success": False,
                    "error": "bad_request",
                    "message": str(e),
                    "contract_address": contract_address,
                    "token_id": token_id
                }
                
            elif status_code == 404:
                logger.warning(f"[WARNING] NFT 未找到: {contract_address}/{token_id}")
                return {
                    "success": False,
                    "error": "not_found",
                    "message": "NFT 不存在或元數據不可用",
                    "contract_address": contract_address,
                    "token_id": token_id
                }
                
            elif status_code == 429:
                logger.warning(f"[WARNING] 達到 NFT API 速率限制 (429): {e}")
                attempts += 1
                last_error = e
                
                if attempts < retry_count:
                    wait_time = retry_delay * (2 ** (attempts - 1))  # 指數增長的等待時間
                    logger.info(f"等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                    continue
                    
                return {
                    "success": False,
                    "error": "rate_limit",
                    "message": "已達到 API 速率限制，所有重試都失敗",
                    "contract_address": contract_address,
                    "token_id": token_id
                }
                
            else:
                logger.error(f"[ERROR] HTTP 錯誤: {e}")
                attempts += 1
                last_error = e
                
                if attempts < retry_count:
                    wait_time = retry_delay * (2 ** (attempts - 1))
                    logger.info(f"等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                    continue
        
        except requests.exceptions.Timeout:
            logger.warning(f"[WARNING] 請求超時")
            attempts += 1
            last_error = "Timeout"
            
            if attempts < retry_count:
                wait_time = retry_delay * (2 ** (attempts - 1))
                logger.info(f"等待 {wait_time} 秒後重試...")
                time.sleep(wait_time)
                continue
                
        except Exception as e:
            logger.error(f"[ERROR] 獲取 NFT 元數據時發生錯誤: {e}")
            attempts += 1
            last_error = e
            
            if attempts < retry_count:
                wait_time = retry_delay * (2 ** (attempts - 1))
                logger.info(f"等待 {wait_time} 秒後重試...")
                time.sleep(wait_time)
                continue
    
    # 如果所有重試都失敗
    logger.error(f"[ERROR] 經過 {retry_count} 次嘗試後無法獲取 NFT 元數據")
    return {
        "success": False,
        "error": "all_retries_failed",
        "message": f"所有重試都失敗: {last_error}",
        "contract_address": contract_address,
        "token_id": token_id
    }

def resolve_ipfs_uri(ipfs_uri, timeout=15):
    """解析 IPFS URI 獲取元數據"""
    if not ipfs_uri:
        logger.error("[ERROR] IPFS URI 為空")
        return None
        
    try:
        # 將 IPFS URI 轉換為 HTTP 網關 URL
        if ipfs_uri.startswith("ipfs://"):
            http_uri = ipfs_uri.replace("ipfs://", "https://ipfs.io/ipfs/")
        elif ipfs_uri.startswith("ipfs:/"):
            http_uri = ipfs_uri.replace("ipfs:/", "https://ipfs.io/ipfs/")
        else:
            http_uri = ipfs_uri
            
        logger.info(f"正在解析 IPFS URI: {ipfs_uri} -> {http_uri}")
        
        # 獲取元數據，設置超時
        response = requests.get(http_uri, timeout=timeout)
        response.raise_for_status()
        
        if "content-type" in response.headers and "application/json" in response.headers["content-type"]:
            logger.info("[SUCCESS] 成功從 IPFS 獲取 JSON 元數據")
            return response.json()
        else:
            logger.info("[SUCCESS] 從 IPFS 獲取了非 JSON 內容")
            return response.content
            
    except requests.exceptions.Timeout:
        logger.warning(f"[WARNING] IPFS 網關超時: {ipfs_uri}")
        
        # 嘗試備用網關
        try:
            alt_gateway = ipfs_uri.replace("ipfs://", "https://cloudflare-ipfs.com/ipfs/")
            logger.info(f"嘗試備用網關: {alt_gateway}")
            
            alt_response = requests.get(alt_gateway, timeout=timeout)
            alt_response.raise_for_status()
            
            if "content-type" in alt_response.headers and "application/json" in alt_response.headers["content-type"]:
                logger.info("[SUCCESS] 成功從備用 IPFS 網關獲取 JSON 元數據")
                return alt_response.json()
            else:
                logger.info("[SUCCESS] 從備用 IPFS 網關獲取了非 JSON 內容")
                return alt_response.content
                
        except Exception as alt_error:
            logger.error(f"[ERROR] 備用網關也失敗: {alt_error}")
            return {"error": "ipfs_timeout", "details": str(alt_error)}
            
    except Exception as e:
        logger.error(f"[ERROR] 解析 IPFS URI 時出錯: {e}")
        return {"error": "ipfs_error", "details": str(e)}

# 示例用法
def nft_metadata_demo():
    logger.info("開始 NFT 元數據演示...")
    
    # 測試幾個知名 NFT
    nfts = [
        # BAYC
        {"contract": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D", "token_id": "1"},
        # CryptoPunks (注意: 這個收藏不遵循標準 ERC-721 接口)
        {"contract": "0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB", "token_id": "1000"},
        # 無效的 NFT
        {"contract": "0x1234567890123456789012345678901234567890", "token_id": "999999"}
    ]
    
    for nft in nfts:
        logger.info(f"獲取 NFT 元數據: {nft['contract']}/{nft['token_id']}")
        
        result = get_nft_metadata(nft['contract'], nft['token_id'])
        
        if result['success']:
            metadata = result['metadata']
            
            # 顯示基本信息
            logger.info(f"名稱: {metadata.get('title', 'N/A')}")
            logger.info(f"描述: {metadata.get('description', 'N/A')[:100]}...")
            
            # 處理 IPFS 圖像
            if metadata.get('media') and metadata['media']:
                for item in metadata['media']:
                    if item.get('gateway'):
                        logger.info(f"圖像網關 URL: {item['gateway']}")
                    if item.get('raw') and "ipfs://" in item['raw']:
                        logger.info(f"原始 IPFS 圖像 URI: {item['raw']}")
            
            # 處理 metadata 字段
            if metadata.get('metadata'):
                if isinstance(metadata['metadata'], dict):
                    if metadata['metadata'].get('attributes'):
                        logger.info(f"屬性數量: {len(metadata['metadata']['attributes'])}")
                        
                    if metadata['metadata'].get('image') and "ipfs://" in metadata['metadata']['image']:
                        ipfs_uri = metadata['metadata']['image']
                        logger.info(f"嘗試解析元數據中的 IPFS 圖像: {ipfs_uri}")
                        # 注意: 在實際應用中，您可能想要解析這個 IPFS URI
                        # ipfs_content = resolve_ipfs_uri(ipfs_uri)
        else:
            logger.warning(f"[WARNING] 獲取 NFT 元數據失敗: {result['error']}")
        
        logger.info("-" * 40)
    
    logger.info("NFT 元數據演示完成")

# 執行演示
if __name__ == "__main__":
    nft_metadata_demo()