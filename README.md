<div align="center">

# Alchemy API Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Alchemy API](https://img.shields.io/badge/Alchemy-API-blue)](https://www.alchemy.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

A production-ready toolkit for working with Alchemy's blockchain APIs, featuring enterprise-grade error handling, intelligent rate limiting, and comprehensive utility functions.
</div>

<details>
<summary>Table of Contents</summary>

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Example Usage](#example-usage)
  - [Basic Usage](#basic-usage)
  - [Advanced Usage](#advanced-usage)
  - [Batch Processing](#batch-processing)
- [Architecture](#architecture)
- [Common Issues & Solutions](#common-issues--solutions)
- [Performance Optimization](#performance-optimization)
- [Contributing](#contributing)
- [Resources](#resources)
- [License](#license)
- [File Structure](#file-structure)

</details>

## Overview

Alchemy API Toolkit is a comprehensive solution designed to streamline interactions with Alchemy's blockchain APIs. Built with both beginners and experienced developers in mind, it eliminates common pain points when working with blockchain data while providing the robustness required for production environments.

## Key Features

✅ **Zero Configuration Setup** - Get started in minutes with sensible defaults  
✅ **Intelligent Rate Limiting** - Automatically adapts to API quotas to prevent throttling  
✅ **Enterprise-Grade Error Handling** - Comprehensive error catching with detailed diagnostics  
✅ **Exponential Backoff Retry** - Resilient request handling for maximum uptime  
✅ **Parallel Processing** - Efficient batch operations for high-throughput applications  
✅ **Extensive Documentation** - Clear examples and comprehensive API references  
✅ **Production Ready** - Thoroughly tested and optimized for real-world applications

## Quick Start

### Prerequisites

- Python 3.7+
- Alchemy API key ([Get one for free here](https://www.alchemy.com/))

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/alchemy-api-toolkit.git
cd alchemy-api-toolkit

# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env with your Alchemy API key
```

## Example Usage

### Basic Usage

Retrieve ETH balance with automatic error handling:

```python
from dotenv import load_dotenv
import os
import logging
from alchemy_api_debug import get_eth_balance
from validate_api_key import is_valid_alchemy_key

# Setup
load_dotenv()
api_key = os.getenv('ALCHEMY_API_KEY')

# Validate API key
if not is_valid_alchemy_key(api_key):
    logging.error("Invalid API key format! Please check your .env file.")
    exit(1)

# Get ETH balance
address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Vitalik's address
balance = get_eth_balance(address)
print(f"Balance: {balance} ETH")
```

### Advanced Usage

Use decorator pattern for retry logic:

```python
from retry_with_backoff import retry_with_backoff
import requests

@retry_with_backoff(max_retries=3, base_delay=1, max_delay=30)
def fetch_data(url):
    """Fetch data with automatic retry on failure"""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

# The function will automatically retry on failure
result = fetch_data("https://api.example.com/data")
```

### Batch Processing

Process multiple requests in parallel with rate limiting:

```python
from examples.batch_processing import process_addresses_in_parallel

# List of addresses to process
addresses = [
    "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
    "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
    "0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8"
]

# Process in parallel with automatic rate limiting
results = process_addresses_in_parallel(addresses, batch_size=5)
```

## Architecture

This toolkit follows a modular architecture designed for flexibility and maintainability:

```
┌─────────────────────────────────────────────────────────────┐
│                     Alchemy API Toolkit                     │
├───────────────┬───────────────┬───────────────┬─────────────┤
│ API Interface │  Reliability  │ Data Process. │   Utility   │
│     Layer     │     Layer     │     Layer     │    Layer    │
├───────────────┼───────────────┼───────────────┼─────────────┤
│ • Alchemy     │ • Rate        │ • Data        │ • Helper    │
│   Endpoints   │   Limiting    │   Parsers     │   Functions │
│ • Request     │ • Retry       │ • Formatters  │ • Common    │
│   Formatting  │   Logic       │ • Validators  │   Operations│
│ • Response    │ • Error       │ • Type        │ • Logging   │
│   Handling    │   Handling    │   Conversion  │   Utilities │
└───────────────┴───────────────┴───────────────┴─────────────┘
```

The toolkit is organized around these core components:

1. **API Interface Layer** - Clean abstractions over Alchemy endpoints
2. **Reliability Layer** - Rate limiting, retry logic, and error handling
3. **Data Processing Layer** - Parsers and formatters for blockchain data
4. **Utility Layer** - Helper functions and common operations

This layered approach ensures separation of concerns and makes the codebase easy to extend and maintain.

## Common Issues & Solutions

| Issue | Solution | Implementation |
|-------|----------|----------------|
| API Rate Limits | Adaptive rate limiting with queue management | `RateLimiter` class with configurable thresholds |
| Transient Network Failures | Exponential backoff with jitter | `@retry_with_backoff` decorator |
| Invalid API Responses | Comprehensive validation and error handling | Type checking and schema validation |
| IPFS Resolution Timeouts | Multi-gateway fallback strategy | Parallel gateway requests with timeout management |
| Inefficient Data Fetching | Batched and parallel processing | Async operations with worker pools |

## Performance Optimization

The toolkit includes several optimizations for high-performance applications:

- **Connection Pooling** - Reuse HTTP connections for faster requests
- **Caching Layer** - Optional in-memory caching to reduce duplicate requests
- **Parallel Processing** - Process multiple requests concurrently
- **Batch Operations** - Combine multiple operations into single API calls
- **Adaptive Timeouts** - Dynamically adjust timeouts based on endpoint performance

## Contributing

We welcome contributions from developers of all skill levels! Here's how to get started:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## Resources

- [Alchemy API Documentation](https://docs.alchemy.com/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Ethereum Developer Resources](https://ethereum.org/developers/)
- [Blockchain Development Best Practices](https://consensys.github.io/smart-contract-best-practices/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## File Structure

```
alchemy-api-toolkit/
├── examples/                  # Ready-to-use example scripts
│   ├── basic_usage.py         # Simple examples for beginners
│   ├── advanced_usage.py      # Advanced patterns and techniques
│   └── batch_processing.py    # Parallel processing examples
├── tests/                     # Comprehensive test suite
├── alchemy_api_debug.py       # Core API interaction module
├── fetch_nft_examples.py      # NFT-specific functionality
├── rate_limiter.py            # Rate limiting implementation
├── retry_with_backoff.py      # Retry logic with exponential backoff
├── test_network_connection.py # Network connectivity utilities
├── validate_api_key.py        # API key validation tools
├── webhook_validator.py       # Webhook security utilities
├── .env.example               # Example environment configuration
├── requirements.txt           # Project dependencies
└── README.md                  # This documentation
```

For detailed API documentation, see our [API Reference](docs/api-reference.md).

---

<div align="center">
  <a href="#top">Back to Top</a> | 
  <a href="https://github.com/your-username/alchemy-api-toolkit/issues/new">Report Issue</a> | 
  <a href="https://github.com/your-username/alchemy-api-toolkit/discussions">Discussions</a>
</div>
