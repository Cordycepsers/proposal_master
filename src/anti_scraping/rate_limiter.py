# src/anti_scraping/rate_limiter.py
import time
from typing import Dict
from .config import config

class RateLimiter:
    """Manages request rate limiting for anti-scraping"""
    
    def __init__(self):
        self.domain_stats: Dict[str, Dict] = {}
        self.max_requests_per_minute = config.MAX_REQUESTS_PER_MINUTE
        self.request_delay_range = config.REQUEST_DELAY_RANGE
    
    def wait_if_needed(self, domain: str) -> None:
        """Wait if rate limit would be exceeded for domain"""
        current_time = time.time()
        
        # Initialize domain stats if needed
        if domain not in self.domain_stats:
            self.domain_stats[domain] = {
                'last_request': 0,
                'request_count': 0,
                'minute_start': current_time
            }
        
        domain_data = self.domain_stats[domain]
        
        # Reset counter if a new minute has started
        if current_time - domain_data['minute_start'] >= 60:
            domain_data['request_count'] = 0
            domain_data['minute_start'] = current_time
        
        # Check if we've hit the rate limit
        if domain_data['request_count'] >= self.max_requests_per_minute:
            wait_time = 60 - (current_time - domain_data['minute_start'])
            if wait_time > 0:
                time.sleep(wait_time)
                # Reset after waiting
                domain_data['request_count'] = 0
                domain_data['minute_start'] = time.time()
        
        # Apply minimum delay between requests
        time_since_last = current_time - domain_data['last_request']
        min_delay = self.request_delay_range[0]
        
        if time_since_last < min_delay:
            wait_time = min_delay - time_since_last
            time.sleep(wait_time)
    
    def record_request(self, domain: str) -> None:
        """Record that a request was made to the domain"""
        current_time = time.time()
        
        if domain not in self.domain_stats:
            self.domain_stats[domain] = {
                'last_request': current_time,
                'request_count': 1,
                'minute_start': current_time
            }
        else:
            self.domain_stats[domain]['last_request'] = current_time
            self.domain_stats[domain]['request_count'] += 1
    
    def get_domain_stats(self, domain: str) -> Dict:
        """Get statistics for a specific domain"""
        return self.domain_stats.get(domain, {})
    
    def reset_domain_stats(self, domain: str) -> None:
        """Reset statistics for a specific domain"""
        if domain in self.domain_stats:
            del self.domain_stats[domain]
