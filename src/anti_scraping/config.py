# src/anti_scraping/config.py
import os
from typing import List, Dict, Optional


class AntiScrapingConfig:
    """Configuration for anti-scraping measures"""

    # User-agent rotation settings
    USER_AGENTS: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ]

    # Proxy settings
    PROXIES: List[Dict[str, str]] = [
        {"http": "http://proxy1:port", "https": "https://proxy1:port"},
        {"http": "http://proxy2:port", "https": "https://proxy2:port"},
        # Add more proxies as needed
    ]

    # Rate limiting settings
    MAX_REQUESTS_PER_MINUTE: int = 30
    REQUEST_DELAY_RANGE: tuple = (1, 3)  # seconds between requests

    # CAPTCHA solving settings
    CAPTCHA_SOLVER_API_KEY: Optional[str] = os.getenv("CAPTCHA_API_KEY", "")
    CAPTCHA_SOLVER_PROVIDER: str = "2captcha"  # or 'anticaptcha'
    CAPTCHA_INITIAL_REQUEST_TIMEOUT: int = 30  # seconds for submission requests
    CAPTCHA_POLLING_REQUEST_TIMEOUT: int = 10  # seconds for polling requests

    # Randomization settings
    RANDOM_DELAY_RANGE: tuple = (0.5, 2.0)  # Additional random delay

    # Session management
    SESSION_TIMEOUT: int = 3600  # seconds


config = AntiScrapingConfig()
