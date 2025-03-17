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
