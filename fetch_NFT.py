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

def get_nfts_for_owner(owner_address, page_size=100, max_pages=None, include_spam=False):
    """獲取地址擁有的所有 NFT，處理分頁和錯誤"""
    
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
            
            # 添加分頁參數 (如果有)
            if next_page_key:
                params["pageKey"] = next_page_key
                
            logger.info(f"獲取 NFT 頁面 {page_count}" + (f" (pageKey: {next_page_key[:10]}...)" if next_page_key else ""))
            
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # 獲取本頁的 NFT
                nfts = data.get("ownedNfts", [])
                all_nfts.extend(nfts)
                
                logger.info(f"獲取到 {len(nfts)} 個 NFT，累計 {len(all_nfts)} 個")
                
                # 檢查是否有下一頁
                next_page_key = data.get("pageKey")
                if not next_page_key:
                    logger.info(f"[SUCCESS] 已獲取所有 NFT，共 {len(all_nfts)} 個")
                    break
                
                # 檢查是否達到最大頁數限制
                if max_pages and page_count >= max_pages:
                    logger.warning(f"[WARNING] 達到最大頁數限制 ({max_pages})，共獲取 {len(all_nfts)} 個 NFT")
                    break
                
                # 添加小延遲，避免速率限制
                time.sleep(0.5)
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                
                if status_code == 400:
                    try:
                        error_detail = e.response.json()
                        logger.error(f"[ERROR] 請求錯誤 (400): {error_detail}")
                    except:
                        logger.error(f"[ERROR] 請求錯誤 (400): {e}")
                    break
                    
                elif status_code == 429:
                    logger.warning(f"[WARNING] 達到速率限制 (429)，等待 2 秒...")
                    time.sleep(2)
                    continue
                    
                else:
                    logger.error(f"[ERROR] HTTP 錯誤: {e}")
                    break
            
            except requests.exceptions.Timeout:
                logger.warning(f"[WARNING] 請求超時，重試...")
                continue
                
            except Exception as e:
                logger.error(f"[ERROR] 獲取 NFT 時發生錯誤: {e}")
                break
        
        return {
            "success": True,
            "nfts": all_nfts,
            "total": len(all_nfts),
            "owner": owner_address,
            "pages_fetched": page_count
        }
        
    except Exception as e:
        logger.error(f"[ERROR] 獲取 NFT 過程中發生未預期的錯誤: {e}")
        return {
            "success": False,
            "error": "unexpected_error",
            "message": str(e),
            "nfts": all_nfts,
            "total": len(all_nfts),
            "owner": owner_address,
            "pages_fetched": page_count
        }

def get_nft_transfers(owner_address, page_size=100, max_pages=1):
    """獲取地址的 NFT 轉移歷史，直接使用 alchemy_getAssetTransfers 端點"""
    
    # 使用 Alchemy JSON-RPC API 端點
    url = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
    
    all_transfers = []
    page_count = 0
    page_key = None
    
    try:
        while True:
            page_count += 1
            
            # 準備 JSON-RPC 請求
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "alchemy_getAssetTransfers",
                "params": [{
                    "fromBlock": "0x0",
                    "toBlock": "latest",
                    "fromAddress": owner_address,  # 僅獲取從此地址發出的轉移
                    "category": ["erc721", "erc1155"],  # 僅 NFT 轉移
                    "maxCount": "0x" + format(page_size, 'x')  # 十六進制格式
                }]
            }
            
            # 添加分頁參數 (如果有)
            if page_key:
                payload["params"][0]["pageKey"] = page_key
                
            logger.info(f"獲取 NFT 轉移歷史頁面 {page_count}" + (f" (pageKey 存在)" if page_key else ""))
            
            try:
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # 檢查結果是否有效
                if "result" not in data or "transfers" not in data["result"]:
                    logger.warning(f"[WARNING] API 返回的數據格式不符預期: {data}")
                    break
                
                # 獲取本頁的轉移記錄
                transfers = data["result"]["transfers"]
                all_transfers.extend(transfers)
                
                logger.info(f"獲取到 {len(transfers)} 筆轉移記錄，累計 {len(all_transfers)} 筆")
                
                # 檢查是否有下一頁
                page_key = data["result"].get("pageKey")
                if not page_key:
                    logger.info(f"[SUCCESS] 已獲取所有轉移記錄，共 {len(all_transfers)} 筆")
                    break
                
                # 檢查是否達到最大頁數限制
                if max_pages and page_count >= max_pages:
                    logger.warning(f"[WARNING] 達到最大頁數限制 ({max_pages})，共獲取 {len(all_transfers)} 筆轉移記錄")
                    break
                
                # 添加小延遲，避免速率限制
                time.sleep(0.5)
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                
                try:
                    error_json = e.response.json()
                    logger.error(f"[ERROR] HTTP 錯誤 {status_code}: {error_json}")
                except:
                    logger.error(f"[ERROR] HTTP 錯誤 {status_code}: {e}")
                
                if status_code == 429:
                    logger.warning(f"[WARNING] 達到速率限制 (429)，等待 2 秒...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"[ERROR] HTTP 錯誤: {e}")
                    break
            
            except Exception as e:
                logger.error(f"[ERROR] 獲取 NFT 轉移歷史時發生錯誤: {e}")
                break
        
        # 處理和格式化轉移記錄
        formatted_transfers = []
        for transfer in all_transfers:
            formatted_transfer = {
                "asset": transfer.get("asset", "N/A"),
                "tokenId": transfer.get("tokenId", "N/A"),
                "from": transfer.get("from", "N/A"),
                "to": transfer.get("to", "N/A"),
                "blockNumber": transfer.get("blockNum", "N/A"),
                "hash": transfer.get("hash", "N/A"),
                "timestamp": transfer.get("metadata", {}).get("blockTimestamp", "N/A"),
                "value": transfer.get("value", 0),
                "category": transfer.get("category", "N/A")
            }
            formatted_transfers.append(formatted_transfer)
        
        return {
            "success": True,
            "transfers": formatted_transfers,
            "total": len(formatted_transfers),
            "owner": owner_address,
            "pages_fetched": page_count
        }
        
    except Exception as e:
        logger.error(f"[ERROR] 獲取 NFT 轉移歷史過程中發生未預期的錯誤: {e}")
        return {
            "success": False,
            "error": "unexpected_error",
            "message": str(e),
            "transfers": [],
            "total": 0,
            "owner": owner_address,
            "pages_fetched": page_count
        }

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
def nft_owner_demo():
    logger.info("開始 NFT 持有者演示...")
    
    # 測試幾個知名地址
    owners = [
        # Vitalik
        "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
        # 一個主要的 NFT 收藏家
        "0x54BE3a794282C030b15E43aE2bB182E14c409C5e"
    ]
    
    for owner in owners:
        logger.info(f"獲取地址 {owner} 的 NFT...")
        
        # 僅獲取第一頁，避免請求太多
        result = get_nfts_for_owner(owner, page_size=10, max_pages=1)
        
        if result['success']:
            logger.info(f"[SUCCESS] 獲取到 {result['total']} 個 NFT (顯示前 {min(5, result['total'])} 個)")
            
            # 顯示前幾個 NFT
            for i, nft in enumerate(result['nfts'][:5]):
                logger.info(f"NFT {i+1}:")
                logger.info(f"  合約: {nft.get('contract', {}).get('address', 'N/A')}")
                logger.info(f"  代幣 ID: {nft.get('id', {}).get('tokenId', 'N/A')}")
                logger.info(f"  名稱: {nft.get('title', 'N/A')}")
                logger.info(f"  Collection: {nft.get('contractMetadata', {}).get('name', 'N/A')}")
                
                # 檢查是否有圖像
                if nft.get('media') and len(nft['media']) > 0 and nft['media'][0].get('gateway'):
                    logger.info(f"  圖像: {nft['media'][0]['gateway']}")
                    
                logger.info("  ------------------")
        else:
            logger.warning(f"[WARNING] 獲取 NFT 失敗: {result.get('error', 'unknown_error')}")
        
        logger.info("-" * 40)
        
        # 獲取轉移歷史
        logger.info(f"獲取地址 {owner} 的 NFT 轉移歷史...")
        transfer_result = get_nft_transfers(owner, page_size=10, max_pages=1)
        
        if transfer_result['success'] and transfer_result['total'] > 0:
            logger.info(f"[SUCCESS] 獲取到 {transfer_result['total']} 筆轉移記錄 (顯示前 {min(3, transfer_result['total'])} 筆)")
            
            # 顯示前幾個轉移記錄
            for i, transfer in enumerate(transfer_result['transfers'][:3]):
                logger.info(f"轉移記錄 {i+1}:")
                logger.info(f"  合約: {transfer.get('asset', 'N/A')}")
                logger.info(f"  代幣 ID: {transfer.get('tokenId', 'N/A')}")
                logger.info(f"  從: {transfer.get('from', 'N/A')}")
                logger.info(f"  到: {transfer.get('to', 'N/A')}")
                logger.info(f"  區塊號: {transfer.get('blockNumber', 'N/A')}")
                logger.info(f"  交易哈希: {transfer.get('hash', 'N/A')}")
                logger.info("  ------------------")
        else:
            if transfer_result['success']:
                logger.info(f"[SUCCESS] 獲取到 {transfer_result['total']} 筆轉移記錄")
            else:
                logger.warning(f"[WARNING] 獲取 NFT 轉移歷史失敗: {transfer_result.get('error', 'unknown_error')}")
        
        logger.info("=" * 50)
    
    logger.info("NFT 持有者演示完成")

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
            logger.info(f"描述: {metadata.get('description', 'N/A')[:100]}..." if metadata.get('description') else "描述: N/A")
            
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
                        logger.info(f"元數據中的 IPFS 圖像: {ipfs_uri}")
        else:
            logger.warning(f"[WARNING] 獲取 NFT 元數據失敗: {result['error']}")
        
        logger.info("-" * 40)
    
    logger.info("NFT 元數據演示完成")

# 執行演示
if __name__ == "__main__":
    nft_owner_demo()
    # 如果你也想執行元數據演示，取消下面這行的註釋
    # nft_metadata_demo()