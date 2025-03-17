<div align="center">

# Alchemy API Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Alchemy API](https://img.shields.io/badge/Alchemy-API-blue)](https://www.alchemy.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

A comprehensive toolkit for working with Alchemy's blockchain APIs, featuring robust error handling, rate limiting, and utility functions.
</div>

<details>
<summary>Table of Contents</summary>

- [Overview](#overview)
- [Why Use This Toolkit?](#why-use-this-toolkit)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Example Usage](#example-usage)
  - [API Key Validation](#api-key-validation)
  - [Retry with Backoff](#retry-with-backoff)
  - [NFT Data Retrieval](#nft-data-retrieval)
- [Architecture](#architecture)
- [Common Issues & Solutions](#common-issues--solutions)
- [Contributing](#contributing)
- [Resources](#resources)
- [License](#license)
- [File Structure](#file-structure)

</details>

## Overview

Alchemy API Toolkit is a comprehensive toolkit designed to simplify interactions with Alchemy blockchain APIs. It provides a robust set of tools for handling common API challenges such as error handling, rate limiting, and retry logic.

## Why Use This Toolkit?

When working with blockchain APIs, developers often face several common challenges:

- Handling API rate limits and throttling
- Implementing reliable error handling and retry logic
- Parsing and validating complex blockchain data
- Optimizing API requests to reduce costs and latency

This toolkit addresses these challenges by providing tested solutions, allowing you to focus on building your blockchain application rather than dealing with the complexities of the underlying APIs.

## Prerequisites

- Python 3.7 or higher
- Alchemy API key ([Register here](https://www.alchemy.com/))
- The following Python libraries:
  - web3
  - requests
  - python-dotenv

## Installation

1. Clone this repository:

```bash
git clone https://github.com/nathan0x-XYZ/alchemy-api-toolkit.git
cd alchemy-api-toolkit
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file and add your Alchemy API key:

```
ALCHEMY_API_KEY=your_api_key_here
```

## Example Usage

### API Key Validation

```python
from validate_api_key import is_valid_alchemy_key
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv('ALCHEMY_API_KEY')

if not is_valid_alchemy_key(api_key):
    print("Invalid API key format! Please check your .env file.")
else:
    print("API key format is valid.")
```

### Retry with Backoff

```python
from retry_with_backoff import retry_with_backoff
import requests

@retry_with_backoff(max_retries=3, backoff_factor=2)
def fetch_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # This will raise an exception on HTTP errors
    return response.json()["ethereum"]["usd"]

# Using the retry decorator
try:
    eth_price = fetch_eth_price()
    print(f"ETH price: ${eth_price}")
except Exception as e:
    print(f"Could not fetch ETH price: {e}")
```

### NFT Data Retrieval

```python
from fetch_nft_examples import get_nfts_for_owner, get_nft_metadata

# Get NFTs owned by an address
owner_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Vitalik's address
result = get_nfts_for_owner(owner_address, page_size=5, max_pages=1)

if result["success"]:
    print(f"Found {result['total']} NFTs")
    
    # If there are NFTs, get metadata for the first one
    if result["nfts"]:
        nft = result["nfts"][0]
        contract_address = nft.get("contract", {}).get("address")
        token_id = nft.get("id", {}).get("tokenId")
        
        if contract_address and token_id:
            metadata_result = get_nft_metadata(contract_address, token_id)
            if metadata_result["success"]:
                print(f"NFT name: {metadata_result['metadata'].get('title', 'Unnamed')}")
else:
    print(f"Failed to get NFTs: {result.get('error', 'Unknown error')}")
```

## Architecture

This toolkit follows a modular design principle, with each component focused on a specific functionality:

<div align="center">
  <img src="https://mermaid.ink/img/pako:eNp1kc1OwzAQhF9l5QsVUvqDlEOlXnIBiUMP3CJfvG2sOnawd1Mq8u7YTlVBwqfZme-bXW8QWCsQMFJlvFKdJd-gNFLhJBWNxkqSbzQZSQPZXpLWWlLnSA_kR_KWWrJjZ7Qk2_eaXKXIkB2oNDRRqUlpZ8jLXlNfNeSdUbQzZGVn6GBLqnRjyVZUWdJGkWu6hpzTVJHvSFvyY9dQcOSNVqQqS6Uj3VJw1Bk7UNiTG7qGYk9uMDWFGxpbCpbsQYcbCi3Vg6ZIrqOxpdhRqA3VZCsKpSZXUhg0uYZCrWkwFNpOk9tRVJpGQ7EzNLaGYjBUa3I7irWh2BsaG0OxMzQOhsZS09hZGgdDY2VpLDWNtaXRGRoHQ-NgaRwsjb2lsR8s_Y_5Oc_-5vkbAAD__5OAXQ" alt="Architecture Diagram" />
</div>

Key components include:

1. **Core API Tools** - Handle direct interactions with Alchemy APIs
2. **Error Handling** - Provide robust error catching and diagnostics
3. **Rate Limiting** - Prevent API throttling and overuse
4. **Retry Logic** - Implement exponential backoff to handle transient failures
5. **Data Parsers** - Simplify handling of complex blockchain data

## Common Issues & Solutions

| Issue | Solution | Code Example |
|------|----------|----------|
| Invalid API key | Check `.env` file and validate key format | `from validate_api_key import is_valid_alchemy_key` |
| Request throttling | Implement rate limiting and backoff strategies | `from rate_limiter import RateLimiter` |
| Network connectivity issues | Use retry mechanisms and check network connection | `from test_network_connection import test_alchemy_connection` |
| IPFS URI resolution failures | Use multiple IPFS gateways and timeout handling | `from fetch_nft_examples import resolve_ipfs_uri` |
| Inefficient batch requests | Use batch API endpoints to reduce request count | `from alchemy_api_debug import batch_get_eth_balances` |

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues.

### Code Style Guidelines

- Use [Black](https://github.com/psf/black) for code formatting
- Add appropriate docstrings
- Include unit tests
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines

## Resources

- [Alchemy API Documentation](https://docs.alchemy.com/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Ethereum Developer Resources](https://ethereum.org/developers/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that allows anyone to use, modify, and distribute this code, even for commercial purposes, as long as the original copyright notice is included.

## File Structure

This toolkit contains the following main components:

| File Name | Description |
|--------|----------|
| `fetch_nft_examples.py` | Complete NFT API toolkit with functions for retrieving NFTs, NFT metadata, and NFT transfer history, as well as IPFS URI resolution |
| `alchemy_api_debug.py` | Alchemy API debugging tools with error handling, retry mechanisms, and batch request capabilities |
| `retry_with_backoff.py` | Exponential backoff retry mechanism for improved API request reliability and resilience |
| `rate_limiter.py` | API rate limiting implementation to prevent API throttling |
| `validate_api_key.py` | API key validation tool using regex pattern matching |
| `test_network_connection.py` | Network connectivity test utility for Alchemy API endpoints |
| `webhook_validator.py` | Webhook signature validation for secure callbacks |

For a more detailed description of each file and its functionality, please see the [File Descriptions](update_file_descriptions.md) document.

Additionally, it includes detailed debugging guides (`alchemy-debug-guide.md` and `alchemy-debug-guide-en.md`) to help you troubleshoot common issues.

---

<div align="center">
  <a href="#top">Back to Top</a>
</div>
