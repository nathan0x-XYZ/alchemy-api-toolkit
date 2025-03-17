# File: retry_with_backoff.py
# Purpose: Implement exponential backoff retry mechanism for API resilience

import time
import random
import requests
from requests.exceptions import RequestException, Timeout

def retry_with_backoff(func, max_retries=5, base_delay=1, max_delay=30):
    """
    Retry a function with exponential backoff strategy
    
    Parameters:
        func: Function to retry
        max_retries (int): Maximum number of retries
        base_delay (float): Initial delay in seconds
        max_delay (float): Maximum delay in seconds
    
    Returns:
        The result of the function if successful
        
    Raises:
        Exception: If maximum retries are reached
    """
    retries = 0
    while True:
        try:
            return func()
        except (RequestException, TimeoutError) as e:
            retries += 1
            if retries > max_retries:
                raise Exception(f"Maximum retries reached ({max_retries}): {str(e)}")
            
            # Calculate delay time (with jitter)
            delay = min(max_delay, base_delay * (2 ** (retries - 1)))
            jitter = random.uniform(0, 0.1 * delay)
            sleep_time = delay + jitter
            
            print(f"Operation failed, retrying in {sleep_time:.2f} seconds (attempt {retries}/{max_retries}): {str(e)}")
            time.sleep(sleep_time)

# Example usage
if __name__ == "__main__":
    # Example function that might fail
    def fetch_data():
        # Simulate a request that might fail
        r = random.random()
        if r < 0.7:  # 70% chance of failure for demonstration
            print("Request failed (simulated)")
            raise RequestException("Simulated request failure")
        return "Data successfully retrieved"
    
    try:
        # Try to fetch data with retry mechanism
        result = retry_with_backoff(fetch_data, max_retries=3, base_delay=1)
        print(f"Success: {result}")
    except Exception as e:
        print(f"Failed after all retries: {e}")
