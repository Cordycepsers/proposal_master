# src/anti_scraping/proxy_manager.py
import random
import requests
from typing import Dict, Optional, List
from .config import config

class ProxyManager:
    """Manages proxy rotation for anti-scraping"""
    
    def __init__(self):
        self.proxies = config.PROXIES.copy()
        self.current_index = 0
        self.failed_proxies = set()
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random working proxy from the pool"""
        available_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        
        if not available_proxies:
            # Reset failed proxies if all are down
            self.failed_proxies.clear()
            available_proxies = self.proxies.copy()
        
        if available_proxies:
            return random.choice(available_proxies)
        return None
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get the next proxy in rotation"""
        if not self.proxies:
            return None
            
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def mark_proxy_as_failed(self, proxy: Dict[str, str]):
        """Mark a proxy as failed"""
        self.failed_proxies.add(proxy)
    
    def is_proxy_working(self, proxy: Dict[str, str]) -> bool:
        """Test if a proxy is working"""
        try:
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def add_proxy(self, http_proxy: str, https_proxy: str):
        """Add a new proxy to the pool"""
        new_proxy = {
            'http': http_proxy,
            'https': https_proxy
        }
        if new_proxy not in self.proxies:
            self.proxies.append(new_proxy)
