# Alchemy API Toolkit

![Alchemy Logo](https://www.alchemy.com/images/alchemylogo.svg)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Alchemy API](https://img.shields.io/badge/Alchemy-API-8A2BE2)](https://docs.alchemy.com/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> A comprehensive toolkit for working with Alchemy APIs, including debugging guides, error handling examples, and production-ready code samples.

<details>
<summary>📖 Table of Contents</summary>

- [Overview](#overview)
- [Why Use This Toolkit?](#why-use-this-toolkit)
- [Contents](#contents)
- [Features](#features)
- [Use Cases](#use-cases)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Example Usage](#example-usage)
  - [API Key Validation](#api-key-validation)
  - [Retry with Backoff](#retry-with-backoff)
  - [NFT Data Retrieval](#nft-data-retrieval)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Common Issues & Solutions](#common-issues--solutions)
- [Contributing](#contributing)
- [Resources](#resources)
- [License](#license)

</details>

## Overview

This repository contains a collection of tools, guides, and code examples for effectively working with Alchemy's blockchain APIs. It is designed to help developers troubleshoot common issues, implement best practices, and build robust applications on top of Alchemy's infrastructure.

## Why Use This Toolkit?

Working with blockchain APIs presents unique challenges:

- **Rate limiting**: Blockchain APIs often have strict rate limits
- **Reliability**: Network congestion can cause intermittent failures
- **Complex data structures**: NFT metadata and blockchain data can be complex
- **Error handling**: Different error types require different handling strategies

This toolkit provides **production-tested solutions** to these challenges, saving you hours of debugging and development time.

## Contents

- [**Debug Guide**](./alchemy-debug-guide-en.md) - Comprehensive guide for troubleshooting Alchemy API integration issues
- **Code Examples**:
  - [API Key Validation](./validate_api_key.py) - Validate Alchemy API keys and check permissions
  - [Network Connection Testing](./test_network_connection.py) - Test connectivity to Alchemy endpoints
  - [Rate Limiting](./rate_limiter.py) - Implement rate limiting to avoid API throttling
  - [Retry with Backoff](./retry_with_backoff.py) - Exponential backoff strategy for handling rate limits
  - [Webhook Validation](./webhook_validator.py) - Validate and process Alchemy webhooks
  - [NFT Data Retrieval](./fetch_nft_examples.py) - Fetch NFT data with pagination and error handling
  - [Complete Error Handling](./alchemy_api_debug.py) - Comprehensive error handling for all API calls

## Features

- ✅ **Production-ready code examples** - Copy and paste into your projects
- ✅ **Comprehensive error handling** - Catch and handle all possible API errors
- ✅ **Rate limit avoidance strategies** - Prevent hitting API rate limits
- ✅ **Webhook integration examples** - Process real-time blockchain events
- ✅ **NFT API implementation patterns** - Handle NFT data with best practices
- ✅ **Detailed debugging guide** - Troubleshoot common issues quickly

## Use Cases

This toolkit is designed for developers who are:

- Building dApps that need reliable blockchain data access
- Implementing NFT functionality in their applications
- Setting up monitoring and alerting for blockchain events
- Troubleshooting API integration issues
- Learning best practices for working with blockchain APIs

## Getting Started

### Prerequisites

- Python 3.7 or higher
- An Alchemy API key ([Get one here](https://dashboard.alchemy.com/))
- Basic understanding of blockchain concepts

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/nathan0x-XYZ/alchemy-api-toolkit.git
   cd alchemy-api-toolkit
   ```

2. Create a `.env` file and add your Alchemy API key:
   ```
   ALCHEMY_API_KEY=your_alchemy_api_key
   ```

3. Install required dependencies:
   ```bash
   pip install web3 requests python-dotenv
   ```

4. Run any of the example scripts:
   ```bash
   python alchemy_api_debug.py
   ```

## Example Usage

### API Key Validation

```python
from validate_api_key import validate_alchemy_key

# Check if your API key is valid and has the required permissions
result = validate_alchemy_key(
    api_key="your_alchemy_api_key",
    required_permissions=["nft_read", "eth_read"]
)

if result["valid"]:
    print(f"API key is valid with permissions: {result['permissions']}")
else:
    print(f"API key validation failed: {result['error']}")
```

### Retry with Backoff

```python
from retry_with_backoff import retry_with_backoff

@retry_with_backoff(max_retries=3, backoff_factor=1.5)
def get_eth_balance(address):
    # This function will automatically retry with exponential backoff
    # if it raises an exception
    response = requests.get(f"{ALCHEMY_API_URL}/getBalance", params={"address": address})
    response.raise_for_status()
    return response.json()
```

### NFT Data Retrieval

```python
from fetch_nft_examples import get_nfts_for_owner

# Get all NFTs owned by an address with pagination handling
nfts = get_nfts_for_owner(
    owner_address="0x123...",
    page_size=100,
    max_pages=None,  # Fetch all pages
    include_spam=False
)

print(f"Found {nfts['total']} NFTs for address {nfts['owner']}")
for nft in nfts['nfts']:
    print(f"NFT: {nft['name']} (ID: {nft['tokenId']})")
```

## Architecture

This toolkit follows these design principles:

```
┌─────────────────────────────────────┐
│           Application Layer          │
│                                     │
│  ┌─────────────┐    ┌─────────────┐ │
│  │   Business   │    │    Error    │ │
│  │    Logic     │    │   Handling  │ │
│  └─────────────┘    └─────────────┘ │
│                                     │
├─────────────────────────────────────┤
│           Middleware Layer           │
│                                     │
│  ┌─────────────┐    ┌─────────────┐ │
│  │ Rate Limiter │    │ Retry Logic │ │
│  └─────────────┘    └─────────────┘ │
│                                     │
├─────────────────────────────────────┤
│            Network Layer             │
│                                     │
│  ┌─────────────┐    ┌─────────────┐ │
│  │  API Client  │    │  Validation │ │
│  └─────────────┘    └─────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

Each component is designed to be:
- **Modular**: Use only what you need
- **Composable**: Combine components as needed
- **Testable**: Each component can be tested in isolation
- **Robust**: Comprehensive error handling at each layer

## Documentation

For detailed information about using the Alchemy API, refer to the [Debug Guide](./alchemy-debug-guide-en.md) included in this repository.

## Common Issues & Solutions

| Issue | Solution | Code Example |
|-------|----------|--------------|
| API Rate Limits | Implement exponential backoff | [retry_with_backoff.py](./retry_with_backoff.py) |
| Invalid API Key | Validate key before use | [validate_api_key.py](./validate_api_key.py) |
| Network Errors | Add proper error handling | [alchemy_api_debug.py](./alchemy_api_debug.py) |
| IPFS Resolution Failures | Use multiple gateways | [fetch_nft_examples.py](./fetch_nft_examples.py) |
| Large NFT Collections | Implement pagination | [fetch_nft_examples.py](./fetch_nft_examples.py) |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

This project follows the [Black](https://github.com/psf/black) code style. Please ensure your contributions are formatted accordingly:

```bash
pip install black
black .
```

## Resources

- [Alchemy Documentation](https://docs.alchemy.com/)
- [Alchemy Dashboard](https://dashboard.alchemy.com/)
- [Alchemy Discord Community](https://discord.gg/alchemyplatform)
- [Web3.py Documentation](https://web3py.readthedocs.io/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that allows anyone to use, modify, and distribute this code, even for commercial purposes, as long as the original copyright notice is included.

---

<div align="center">

**[⬆ back to top](#alchemy-api-toolkit)**

*Created with ❤️ for the blockchain developer community*

</div>
