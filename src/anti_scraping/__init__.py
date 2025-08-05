"""
Anti-Scraping Module for Proposal Master System

This module provides comprehensive anti-scraping and web scraping protection
mechanisms including user-agent rotation, proxy management, rate limiting,
CAPTCHA solving, and intelligent request handling.

Components:
- UserAgentManager: Manages user-agent rotation and browser fingerprinting
- ProxyManager: Handles proxy rotation and management
- RateLimiter: Implements intelligent rate limiting strategies
- CaptchaSolver: Integrates with CAPTCHA solving services
- RequestHandler: Main request handler with all anti-scraping measures
- Config: Configuration management for anti-scraping settings
"""

from .config import config, AntiScrapingConfig
from .user_agent_manager import UserAgentManager
from .proxy_manager import ProxyManager
from .rate_limiter import RateLimiter
from .captcha_solver import CaptchaSolver
from .request_handler import RequestHandler

__version__ = "1.0.0"
__author__ = "Proposal Master Team"

__all__ = [
    "config",
    "AntiScrapingConfig",
    "UserAgentManager",
    "ProxyManager", 
    "RateLimiter",
    "CaptchaSolver",
    "RequestHandler"
]
