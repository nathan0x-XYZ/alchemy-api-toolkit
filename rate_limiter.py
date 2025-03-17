# File: rate_limiter.py
# Purpose: Add rate limiting implementation to prevent API throttling

import time
import threading

class RateLimiter:
    """
    A class to track and limit API call rates
    
    This class helps prevent hitting API rate limits by tracking
    the number of calls made within a specified time frame.
    """
    def __init__(self, max_calls, time_frame):
        """
        Initialize the rate limiter
        
        Args:
            max_calls (int): Maximum number of calls allowed within the time frame
            time_frame (float): Time frame in seconds
        """
        self.max_calls = max_calls  # Maximum number of calls allowed within the time frame
        self.time_frame = time_frame  # Time frame in seconds
        self.calls = []  # Record of call timestamps
        self.lock = threading.Lock()
        
    def can_call(self):
        """
        Check if an API call can be made
        
        Returns:
            bool: True if a call can be made, False otherwise
        """
        with self.lock:
            now = time.time()
            # Remove call records outside the time frame
            self.calls = [t for t in self.calls if now - t < self.time_frame]
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False
    
    def wait_time(self):
        """
        Return the time to wait before making the next call
        
        Returns:
            float: Time to wait in seconds
        """
        with self.lock:
            if len(self.calls) < self.max_calls:
                return 0
            
            now = time.time()
            oldest_call = min(self.calls)
            return max(0, self.time_frame - (now - oldest_call))
    
    def wait_if_needed(self):
        """
        Wait if rate limit is reached before making a call
        
        This method will block until a call can be made without
        exceeding the rate limit.
        
        Returns:
            float: The time waited in seconds
        """
        wait_time = self.wait_time()
        if wait_time > 0:
            time.sleep(wait_time)
            # After waiting, register the call
            with self.lock:
                now = time.time()
                self.calls = [t for t in self.calls if now - t < self.time_frame]
                self.calls.append(now)
            return wait_time
        
        # If we can make a call without waiting, register it
        if self.can_call():
            return 0
        
        # If we reach here, something changed between wait_time and can_call
        # Try again recursively (should be rare)
        return self.wait_if_needed()

# Example usage
if __name__ == "__main__":
    # Create a rate limiter with 5 calls per 10 seconds
    limiter = RateLimiter(max_calls=5, time_frame=10)
    
    # Simulate API calls
    for i in range(10):
        if limiter.can_call():
            print(f"Call {i+1}: API call made")
        else:
            wait_time = limiter.wait_time()
            print(f"Call {i+1}: Rate limit reached. Wait {wait_time:.2f} seconds")
            time.sleep(wait_time)
            # Try again after waiting
            if limiter.can_call():
                print(f"Call {i+1}: API call made after waiting")
        
        # Simulate some processing time
        time.sleep(0.5)
    
    # Example of using wait_if_needed
    print("\nExample of using wait_if_needed:")
    for i in range(5):
        wait_time = limiter.wait_if_needed()
        if wait_time > 0:
            print(f"Call {i+1}: Waited {wait_time:.2f} seconds before making API call")
        else:
            print(f"Call {i+1}: API call made without waiting")
        time.sleep(0.5)
