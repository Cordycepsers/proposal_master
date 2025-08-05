# src/anti_scraping/user_agent_manager.py
import random
from typing import List
from .config import config

class UserAgentManager:
    """Manages user-agent rotation for anti-scraping"""
    
    def __init__(self):
        self.user_agents = config.USER_AGENTS.copy()
        self.current_index = 0
    
    def get_random_user_agent(self) -> str:
        """Get a random user-agent from the pool"""
        return random.choice(self.user_agents)
    
    def get_next_user_agent(self) -> str:
        """Get the next user-agent in rotation"""
        user_agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return user_agent
    
    def add_user_agent(self, user_agent: str):
        """Add a new user-agent to the pool"""
        if user_agent not in self.user_agents:
            self.user_agents.append(user_agent)
    
    def get_user_agents_count(self) -> int:
        """Get total number of user-agents"""
        return len(self.user_agents)
