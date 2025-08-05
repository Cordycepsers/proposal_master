# src/anti_scraping/captcha_solver.py
import requests
import time
import json
from typing import Dict, Optional
from .config import config

class CaptchaSolver:
    """Handles CAPTCHA solving integration"""
    
    def __init__(self):
        self.api_key = config.CAPTCHA_SOLVER_API_KEY
        self.provider = config.CAPTCHA_SOLVER_PROVIDER.lower()
        
        if not self.api_key:
            raise ValueError("CAPTCHA API key is required")
    
    def solve_recaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA using the configured provider"""
        try:
            if self.provider == '2captcha':
                return self._solve_with_2captcha(site_key, page_url)
            elif self.provider == 'anticaptcha':
                return self._solve_with_anticaptcha(site_key, page_url)
            else:
                raise ValueError(f"Unsupported CAPTCHA provider: {self.provider}")
        except Exception as e:
            print(f"CAPTCHA solving failed: {str(e)}")
            return None
    
    def _solve_with_2captcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve CAPTCHA using 2captcha API"""
        url = "http://2captcha.com/in.php"
        
        payload = {
            'key': self.api_key,
            'method': 'userrecaptcha',
            'googlekey': site_key,
            'pageurl': page_url,
            'json': 1
        }
        
        response = requests.post(url, data=payload)
        result = response.json()
        
        if result.get('status') == 1:
            captcha_id = result.get('request')
            
            # Poll for solution
            poll_url = "http://2captcha.com/res.php"
            poll_payload = {
                'key': self.api_key,
                'action': 'get',
                'id': captcha_id,
                'json': 1
            }
            
            while True:
                poll_response = requests.get(poll_url, params=poll_payload)
                poll_result = poll_response.json()
                
                if poll_result.get('status') == 1:
                    return poll_result.get('request')
                
                time.sleep(5)  # Wait 5 seconds before polling again
        return None
    
    def _solve_with_anticaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve CAPTCHA using Anticaptcha API"""
        url = "https://api.anti-captcha.com/createTask"
        
        payload = {
            "clientKey": self.api_key,
            "task": {
                "type": "RecaptchaV2TaskProxyless",
                "websiteURL": page_url,
                "websiteKey": site_key
            }
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        if result.get('errorId') == 0:
            task_id = result.get('taskId')
            
            # Poll for solution
            poll_url = "https://api.anti-captcha.com/getTaskResult"
            poll_payload = {
                "clientKey": self.api_key,
                "taskId": task_id
            }
            
            while True:
                poll_response = requests.post(poll_url, json=poll_payload)
                poll_result = poll_response.json()
                
                if poll_result.get('status') == 'ready':
                    return poll_result.get('solution', {}).get('gRecaptchaResponse')
                
                time.sleep(5)  # Wait 5 seconds before polling again
        return None
    
    def solve_image_captcha(self, image_url: str) -> Optional[str]:
        """Solve image CAPTCHA"""
        # Implementation for image CAPTCHA solving
        pass
