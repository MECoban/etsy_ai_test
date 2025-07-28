"""
Rate limiting utilities for Etsy AI Assistant
"""
import streamlit as st
import time


class RateLimiter:
    def __init__(self, max_requests=60, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        if 'rate_limit_requests' not in st.session_state:
            st.session_state['rate_limit_requests'] = []
    
    def can_make_request(self):
        """Check if a request can be made within rate limits"""
        now = time.time()
        # Remove old requests outside the window
        st.session_state['rate_limit_requests'] = [
            req_time for req_time in st.session_state['rate_limit_requests'] 
            if now - req_time < self.window_seconds
        ]
        
        return len(st.session_state['rate_limit_requests']) < self.max_requests
    
    def record_request(self):
        """Record a new request"""
        st.session_state['rate_limit_requests'].append(time.time())
    
    def get_wait_time(self):
        """Get how long to wait before next request"""
        if self.can_make_request():
            return 0
        
        oldest_request = min(st.session_state['rate_limit_requests'])
        return self.window_seconds - (time.time() - oldest_request)
    
    def get_remaining_requests(self):
        """Get number of remaining requests in current window"""
        now = time.time()
        recent_requests = [
            req_time for req_time in st.session_state['rate_limit_requests'] 
            if now - req_time < self.window_seconds
        ]
        return max(0, self.max_requests - len(recent_requests))


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=30, window_seconds=60)  # 30 requests per minute


def throttled_api_call(func, *args, **kwargs):
    """Make API call with rate limiting"""
    if not rate_limiter.can_make_request():
        wait_time = rate_limiter.get_wait_time()
        
        # Show rate limit warning
        st.warning(f"⏱️ Rate limit reached. Please wait {wait_time:.1f} seconds before next request.")
        
        # If wait time is reasonable, wait and proceed
        if wait_time <= 5:  # Only wait if less than 5 seconds
            time.sleep(wait_time)
        else:
            # Import locally to avoid circular dependency
            import importlib
            error_module = importlib.import_module('utils.error_handler')
            APIError = error_module.APIError
            raise APIError(f"Rate limit exceeded. Please wait {wait_time:.1f} seconds.")
    
    # Record the request
    rate_limiter.record_request()
    
    # Make the actual API call
    return func(*args, **kwargs)


def get_rate_limit_status():
    """Get current rate limit status"""
    remaining = rate_limiter.get_remaining_requests()
    wait_time = rate_limiter.get_wait_time()
    
    return {
        'remaining_requests': remaining,
        'max_requests': rate_limiter.max_requests,
        'wait_time': wait_time,
        'percentage_used': ((rate_limiter.max_requests - remaining) / rate_limiter.max_requests) * 100
    } 