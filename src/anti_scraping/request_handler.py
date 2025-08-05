# src/anti_scraping/request_handler.py
import requests
import time
import random
from typing import Dict, Optional, Any
from .user_agent_manager import UserAgentManager
from .proxy_manager import ProxyManager
from .rate_limiter import RateLimiter
from .captcha_solver import CaptchaSolver

class RequestHandler:
    """Main request handler with anti-scraping measures"""
    
    def __init__(self):
        self.user_agent_manager = UserAgentManager()
        self.proxy_manager = ProxyManager()
        self.rate_limiter = RateLimiter()
        self.captcha_solver = CaptchaSolver()
        
    def make_request(self, 
                    url: str, 
                    method: str = 'GET', 
                    headers: Optional[Dict[str, str]] = None,
                    **kwargs) -> Optional[requests.Response]:
        """
        Make HTTP request with anti-scraping measures
        """
        # Wait if rate limit is exceeded
        self.rate_limiter.wait_if_needed()
        
        # Get random user-agent
        user_agent = self.user_agent_manager.get_random_user_agent()
        
        # Get random proxy
        proxy = self.proxy_manager.get_random_proxy()
        
        # Set default headers
        default_headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if headers:
            default_headers.update(headers)
        
        # Add random delay before request
        delay = random.uniform(*self.rate_limiter.random_delay_range)
        time.sleep(delay)
        
        # Make the request
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=default_headers,
                proxies=proxy,
                timeout=30,
                **kwargs
            )
            
            # Check if CAPTCHA was encountered
            if self._is_captcha_encountered(response):
                print("CAPTCHA detected, attempting to solve...")
                captcha_solution = self._attempt_captcha_solve(url)
                if captcha_solution:
                    # Retry with CAPTCHA solution
                    return self._retry_with_captcha_solution(url, captcha_solution)
            
            # Record the request
            self.rate_limiter.make_request()
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if proxy:
                self.proxy_manager.mark_proxy_as_failed(proxy)
            raise
    
    def _is_captcha_encountered(self, response: requests.Response) -> bool:
        """Check if CAPTCHA was encountered"""
        captcha_indicators = [
            'captcha',
            'recaptcha',
            'hcaptcha',
            'sentry',
            'cloudflare'
        ]
        
        content_lower = response.text.lower()
        for indicator in captcha_indicators:
            if indicator in content_lower:
                return True
        return False
    
    def _attempt_captcha_solve(self, page_url: str) -> Optional[str]:
        """Attempt to solve CAPTCHA"""
        # This is a simplified version - real implementation would extract 
        # site key from the page and pass it to solver
        print("CAPTCHA solving not implemented in this example")
        return None
    
    def _retry_with_captcha_solution(self, url: str, solution: str) -> Optional[requests.Response]:
        """Retry request with CAPTCHA solution"""
        # Implementation would depend on specific CAPTCHA type and site requirements
        pass
    
    def get_random_delay(self) -> float:
        """Get random delay between requests"""
        return random.uniform(1.0, 5.0)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current anti-scraping statistics"""
        return {
            'user_agents_count': self.user_agent_manager.get_user_agents_count(),
            'proxies_count': len(self.proxy_manager.proxies),
            'failed_proxies': len(self.proxy_manager.failed_proxies),
            'requests_per_minute': self.rate_limiter.get_requests_per_minute()
        }
