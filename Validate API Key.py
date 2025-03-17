# File: Validate API Key.py
# Purpose: Add comprehensive API key validator with logging capabilities

import re
import os
import logging
from dotenv import load_dotenv

# 設定記錄
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

def is_valid_alchemy_key(api_key):
    """Check if API key format is valid"""
    if api_key is None:
        return False
    pattern = r'^[a-zA-Z0-9_-]{32,}$'
    return bool(re.match(pattern, api_key))

# Usage example
api_key = os.getenv('ALCHEMY_API_KEY')
if not is_valid_alchemy_key(api_key):
    logger.error(f"Invalid API key format or key not found: {api_key}")
else:
    logger.info("API key format is valid")
