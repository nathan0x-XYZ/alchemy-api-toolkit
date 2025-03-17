<!-- File: alchemy-debug-guide.md -->
<!-- Purpose: Add comprehensive debugging guide for Alchemy API (Chinese version) -->

# Alchemy API Debug 指南

## 目錄
- [常見錯誤代碼及解決方案](#常見錯誤代碼及解決方案)
- [API 連線問題排查](#api-連線問題排查)
- [如何避免 API 速率限制](#如何避免-api-速率限制)
- [最佳錯誤處理實踐](#最佳錯誤處理實踐)
- [Python 範例：捕捉與處理 API 錯誤](#python-範例捕捉與處理-api-錯誤)

## 常見錯誤代碼及解決方案

### 403 Forbidden
**問題原因**：
- API 金鑰無效或已過期
- API 金鑰權限不足
- IP 地址被封鎖
- 訂閱計劃限制

**解決方案**：
1. **驗證 API 金鑰**：確認您使用的 API 金鑰正確且未過期
   ```python
   # 檢查 API 金鑰格式
   import re
   def is_valid_alchemy_key(api_key):
       pattern = r'^[a-zA-Z0-9_-]{32,}$'
       return bool(re.match(pattern, api_key))
   ```

2. **檢查計劃限制**：確認您的訂閱計劃支援您嘗試訪問的 API 功能
3. **聯繫 Alchemy 支援**：如果確認 API 金鑰正確但仍遇到 403 錯誤，請聯繫 Alchemy 支援

### 429 Too Many Requests
**問題原因**：
- 超出 API 速率限制
- 短時間內發送過多請求
- 未正確實施退避策略

**解決方案**：
1. **實施指數退避**：當遇到 429 錯誤時，使用指數退避重試策略
2. **批量請求**：將多個單一請求合併成批量請求
3. **使用緩存**：緩存常用數據以減少 API 調用次數
4. **監控使用情況**：定期監控您的 API 使用情況，避免達到限制

### 500 Internal Server Error
**問題原因**：
- Alchemy 服務器問題
- 網絡連接問題
- 請求格式錯誤

**解決方案**：
1. **重試請求**：使用退避策略自動重試請求
2. **檢查請求格式**：確保請求格式正確，特別是 JSON-RPC 參數
3. **聯繫支援**：如果問題持續存在，聯繫 Alchemy 支援並提供詳細錯誤信息

## API 連線問題排查

### 連接超時問題
連接超時通常是由網絡問題或 Alchemy 服務器負載過高引起的。

**排查步驟**：
1. **測試網絡連接**
   ```python
   import requests
   import time
   
   def test_network_connection():
       try:
           start_time = time.time()
           response = requests.get('https://dashboard.alchemy.com/health', timeout=5)
           response_time = time.time() - start_time
           
           print(f"網絡連接狀態: {response.status_code}")
           print(f"響應時間: {response_time:.2f}秒")
           return response.status_code == 200
       except requests.exceptions.RequestException as e:
           print(f"網絡連接測試失敗: {e}")
           return False
   ```

2. **檢查 Alchemy 狀態頁面**
   確認 Alchemy 服務是否有已知中斷或維護
   訪問: https://status.alchemy.com

3. **嘗試不同的節點 URL**
   如果您使用特定網絡（如 Ethereum Mainnet），嘗試其他網絡的節點

### 連接被拒絕問題
如果 API 連接被拒絕，這可能是由於防火牆設置或 IP 限制。

**排查步驟**：
1. **檢查 IP 白名單**：確認您的 IP 地址已添加到 Alchemy 儀表板的白名單中
2. **檢查 VPN/代理**：如果使用 VPN 或代理，嘗試禁用它們
3. **檢查防火牆設置**：確保防火牆未阻止與 Alchemy API 的連接

## 如何避免 API 速率限制

### 實施速率限制追踪器
```python
import time
import threading

class RateLimiter:
    def __init__(self, max_calls, time_frame):
        self.max_calls = max_calls  # 時間框架內允許的最大調用次數
        self.time_frame = time_frame  # 時間框架（秒）
        self.calls = []  # 調用時間戳記錄
        self.lock = threading.Lock()
        
    def can_call(self):
        """檢查是否可以進行 API 調用"""
        with self.lock:
            now = time.time()
            # 移除時間框架外的調用記錄
            self.calls = [t for t in self.calls if now - t < self.time_frame]
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False
    
    def wait_time(self):
        """返回需要等待的時間（秒）"""
        with self.lock:
            if len(self.calls) < self.max_calls:
                return 0
            
            now = time.time()
            oldest_call = min(self.calls)
            return max(0, self.time_frame - (now - oldest_call))
```

### 最佳實踐
1. **使用批量查詢**：合併多個請求以減少 API 調用
   ```python
   # 單獨查詢多個地址餘額
   # 不推薦
   balances = []
   for address in addresses:
       balance = web3.eth.get_balance(address)
       balances.append(balance)
   
   # 使用批量查詢
   # 推薦
   batch_payload = [
       {"jsonrpc": "2.0", "id": i, "method": "eth_getBalance", "params": [addr, "latest"]} 
       for i, addr in enumerate(addresses)
   ]
   response = requests.post(ALCHEMY_URL, json=batch_payload)
   batch_results = response.json()
   ```

2. **實施緩存機制**：緩存常用數據以減少請求數量
   ```python
   import functools

   @functools.lru_cache(maxsize=128)
   def get_transaction(tx_hash):
       """獲取交易詳情（帶緩存）"""
       return web3.eth.get_transaction(tx_hash)
   ```

3. **使用 Webhook 代替輪詢**：設置 Alchemy Webhook 接收事件通知，而不是頻繁輪詢

4. **實施退避策略**：當接近速率限制時，延長請求間隔

## 最佳錯誤處理實踐

### 實施重試機制

使用指數退避重試策略處理臨時錯誤：

```python
import time
import random
from requests.exceptions import RequestException

def retry_with_backoff(func, max_retries=5, base_delay=1, max_delay=30):
    """
    使用指數退避策略重試函數
    
    參數:
        func: 要重試的函數
        max_retries: 最大重試次數
        base_delay: 初始延遲（秒）
        max_delay: 最大延遲（秒）
    """
    retries = 0
    while True:
        try:
            return func()
        except (RequestException, TimeoutError) as e:
            retries += 1
            if retries > max_retries:
                raise Exception(f"已達到最大重試次數 ({max_retries}): {str(e)}")
            
            # 計算延遲時間（帶抖動）
            delay = min(max_delay, base_delay * (2 ** (retries - 1)))
            jitter = random.uniform(0, 0.1 * delay)
            sleep_time = delay + jitter
            
            print(f"操作失敗，將在 {sleep_time:.2f} 秒後重試 (嘗試 {retries}/{max_retries}): {str(e)}")
            time.sleep(sleep_time)
```

### Webhook Debug 技巧

當使用 Alchemy Webhook 時，以下是一些調試技巧：

1. **使用臨時 Webhook 測試服務**：
   - [Webhook.site](https://webhook.site) - 提供臨時 URL 用於測試
   - [Pipedream](https://pipedream.com) - 可用於調試 Webhook 請求

2. **本地開發測試**：
   - 使用 [ngrok](https://ngrok.com) 將本地服務器暴露到互聯網
   ```bash
   # 啟動 ngrok 轉發到本地端口
   ngrok http 3000
   ```

3. **驗證 Webhook 請求**：
   ```python
   from flask import Flask, request, jsonify
   import hmac
   import hashlib
   
   app = Flask(__name__)
   
   @app.route('/webhook', methods=['POST'])
   def handle_webhook():
       # 獲取請求頭中的簽名
       signature = request.headers.get('x-alchemy-signature', '')
       
       # 獲取請求體
       payload = request.data
       
       # 使用您的 Webhook 密鑰計算簽名
       webhook_secret = 'your_webhook_secret'
       expected_signature = hmac.new(
           webhook_secret.encode(),
           payload,
           hashlib.sha256
       ).hexdigest()
       
       # 驗證簽名
       if signature != expected_signature:
           return jsonify({"error": "Invalid signature"}), 403
       
       # 處理 Webhook 數據
       webhook_data = request.json
       print(f"收到 Webhook: {webhook_data}")
       
       return jsonify({"status": "success"}), 200
   
   if __name__ == '__main__':
       app.run(port=3000)
   ```

4. **記錄並監控 Webhook 調用**：
   - 設置詳細的日誌記錄
   - 監控 Webhook 響應時間和錯誤率

## Python 範例：捕捉與處理 API 錯誤

### 完整的 Alchemy API 錯誤處理範例

```python
import os
import time
import requests
import logging
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError
from web3 import Web3
from dotenv import load_dotenv

# 設置日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("alchemy_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("alchemy_api")

# 加載環境變量
load_dotenv()
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')
ALCHEMY_URL = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

# 初始化 Web3
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

def handle_alchemy_error(error, endpoint):
    """處理 Alchemy API 錯誤並提供有用的調試信息"""
    if isinstance(error, HTTPError):
        status_code = error.response.status_code
        if status_code == 403:
            logger.error(f"API 授權錯誤 (403): 檢查 API 金鑰和權限 - {endpoint}")
            logger.debug(f"響應內容: {error.response.text}")
        elif status_code == 429:
            logger.warning(f"達到速率限制 (429): 實施退避策略 - {endpoint}")
            logger.debug(f"響應內容: {error.response.text}")
            # 返回需要退避的信號
            return True
        elif status_code >= 500:
            logger.error(f"Alchemy 服務器錯誤 ({status_code}): 稍後重試 - {endpoint}")
            logger.debug(f"響應內容: {error.response.text}")
            # 返回需要退避的信號
            return True
        else:
            logger.error(f"HTTP 錯誤 ({status_code}): {error} - {endpoint}")
    elif isinstance(error, Timeout):
        logger.error(f"請求超時: {error} - {endpoint}")
        return True
    elif isinstance(error, ConnectionError):
        logger.error(f"連接錯誤: {error} - {endpoint}")
        return True
    elif isinstance(error, RequestException):
        logger.error(f"請求異常: {error} - {endpoint}")
        return True
    else:
        logger.error(f"未知錯誤: {error} - {endpoint}")
    
    return False

def get_eth_balance(address, max_retries=5):
    """獲取 ETH 餘額，帶有錯誤處理和重試機制"""
    endpoint = f"eth_getBalance - {address}"
    retries = 0
    base_delay = 1
    
    while retries <= max_retries:
        try:
            balance = w3.eth.get_balance(address)
            return Web3.from_wei(balance, 'ether')
            
        except Exception as e:
            # 處理錯誤並檢查是否需要退避
            need_backoff = handle_alchemy_error(e, endpoint)
            
            retries += 1
            if retries > max_retries:
                logger.error(f"已達到最大重試次數 ({max_retries}): {address}")
                raise
            
            if need_backoff:
                # 計算退避延遲（帶抖動）
                delay = min(30, base_delay * (2 ** (retries - 1)))
                jitter = delay * 0.1 * (2 * (0.5 - 0.5))  # 在 ±10% 範圍內添加抖動
                sleep_time = delay + jitter
                
                logger.info(f"退避延遲 {sleep_time:.2f} 秒，重試 {retries}/{max_retries}")
                time.sleep(sleep_time)
            else:
                # 對於不需要退避的錯誤，立即重試
                logger.info(f"立即重試 {retries}/{max_retries}")

def batch_get_eth_balances(addresses):
    """批量獲取多個地址的 ETH 餘額"""
    try:
        # 準備批量請求
        batch_payload = [
            {
                "jsonrpc": "2.0", 
                "id": i, 
                "method": "eth_getBalance", 
                "params": [addr, "latest"]
            } 
            for i, addr in enumerate(addresses)
        ]
        
        # 發送批量請求
        response = requests.post(ALCHEMY_URL, json=batch_payload)
        response.raise_for_status()  # 檢查 HTTP 錯誤
        results = response.json()
        
        # 處理結果
        balances = {}
        for i, addr in enumerate(addresses):
            result = next((r for r in results if r["id"] == i), None)
            if result and "result" in result:
                balances[addr] = Web3.from_wei(int(result["result"], 16), 'ether')
            else:
                logger.warning(f"無法獲取地址 {addr} 的餘額")
                balances[addr] = None
        
        return balances
        
    except Exception as e:
        handle_alchemy_error(e, "batch_get_eth_balances")
        raise

def main():
    """主函數，演示 API 錯誤處理"""
    try:
        # 範例 1: 獲取單個地址餘額
        address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Vitalik 的地址
        balance = get_eth_balance(address)
        logger.info(f"地址 {address} 的 ETH 餘額: {balance}")
        
        # 範例 2: 批量獲取多個地址餘額
        addresses = [
            "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # Vitalik
            "0x00000000219ab540356cBB839Cbe05303d7705Fa",  # ETH2 存款合約
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"   # WETH 合約
        ]
        balances = batch_get_eth_balances(addresses)
        for addr, bal in balances.items():
            logger.info(f"地址 {addr} 的 ETH 餘額: {bal}")
            
    except Exception as e:
        logger.error(f"程序執行錯誤: {e}")

if __name__ == "__main__":
    main()
```

### 如何使用

1. 創建 `.env` 文件，添加您的 Alchemy API 密鑰：
   ```
   ALCHEMY_API_KEY=your_alchemy_api_key
   ```

2. 安裝所需的依賴：
   ```bash
   pip install web3 requests python-dotenv
   ```

3. 運行範例：
   ```bash
   python alchemy_api_debug.py
   ```

### 擴展建議

- **添加更多專門的錯誤處理函數**：為不同類型的 API 調用創建特定的錯誤處理器
- **實施更高級的退避策略**：根據不同錯誤類型調整退避參數
- **添加指標收集**：記錄 API 調用成功率、響應時間等指標
- **實施斷路器模式**：在 API 持續失敗時暫時中斷請求
