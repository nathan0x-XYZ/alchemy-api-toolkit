import re

def is_valid_alchemy_key(api_key):
    """
    Validates the format of an Alchemy API key
    
    Args:
        api_key (str): The API key to validate
        
    Returns:
        bool: True if the key format is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9_-]{32,}$'
    return bool(re.match(pattern, api_key))

# Example usage
if __name__ == "__main__":
    # Replace with your actual API key to test
    test_key = "your_alchemy_api_key"
    is_valid = is_valid_alchemy_key(test_key)
    print(f"API key validation result: {is_valid}")
