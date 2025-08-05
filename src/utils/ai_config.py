"""
Configuration for AI services integration.

This module provides configuration and factory methods for 
integrating with various AI services like OpenAI, Anthropic, etc.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class AIServiceConfig:
    """Configuration for AI service integration."""
    service_type: str  # 'openai', 'anthropic', 'azure', 'custom'
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model_name: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 30


class AIServiceFactory:
    """Factory for creating AI service clients."""
    
    @staticmethod
    def create_client(config: AIServiceConfig):
        """Create an AI service client based on configuration."""
        
        if config.service_type == 'openai':
            return AIServiceFactory._create_openai_client(config)
        elif config.service_type == 'anthropic':
            return AIServiceFactory._create_anthropic_client(config)
        elif config.service_type == 'azure':
            return AIServiceFactory._create_azure_client(config)
        else:
            raise ValueError(f"Unsupported AI service type: {config.service_type}")
    
    @staticmethod
    def _create_openai_client(config: AIServiceConfig):
        """Create OpenAI client."""
        try:
            import openai
            
            client = openai.AsyncOpenAI(
                api_key=config.api_key or os.getenv('OPENAI_API_KEY'),
                base_url=config.api_base,
                timeout=config.timeout
            )
            
            # Add configuration to client
            client.config = config
            return client
            
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    @staticmethod
    def _create_anthropic_client(config: AIServiceConfig):
        """Create Anthropic client."""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(
                api_key=config.api_key or os.getenv('ANTHROPIC_API_KEY'),
                timeout=config.timeout
            )
            
            client.config = config
            return client
            
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
    
    @staticmethod
    def _create_azure_client(config: AIServiceConfig):
        """Create Azure OpenAI client."""
        try:
            import openai
            
            client = openai.AsyncAzureOpenAI(
                api_key=config.api_key or os.getenv('AZURE_OPENAI_API_KEY'),
                api_version="2024-02-01",
                azure_endpoint=config.api_base or os.getenv('AZURE_OPENAI_ENDPOINT'),
                timeout=config.timeout
            )
            
            client.config = config
            return client
            
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")


# Default configurations for different services
DEFAULT_CONFIGS = {
    'openai': AIServiceConfig(
        service_type='openai',
        model_name='gpt-4',
        temperature=0.1,
        max_tokens=4000
    ),
    
    'anthropic': AIServiceConfig(
        service_type='anthropic',
        model_name='claude-3-sonnet-20240229',
        temperature=0.1,
        max_tokens=4000
    ),
    
    'azure': AIServiceConfig(
        service_type='azure',
        model_name='gpt-4',
        temperature=0.1,
        max_tokens=4000
    )
}


def get_default_ai_client(service_type: str = 'openai'):
    """Get a default AI client for the specified service."""
    if service_type not in DEFAULT_CONFIGS:
        raise ValueError(f"No default config for service type: {service_type}")
    
    config = DEFAULT_CONFIGS[service_type]
    return AIServiceFactory.create_client(config)


# Example usage and setup instructions
SETUP_INSTRUCTIONS = """
AI Service Setup Instructions:

1. OPENAI SETUP:
   - Install: pip install openai
   - Set environment variable: OPENAI_API_KEY=your_api_key
   - Or pass api_key directly to AIServiceConfig

2. ANTHROPIC SETUP:
   - Install: pip install anthropic  
   - Set environment variable: ANTHROPIC_API_KEY=your_api_key
   - Or pass api_key directly to AIServiceConfig

3. AZURE OPENAI SETUP:
   - Install: pip install openai
   - Set environment variables:
     - AZURE_OPENAI_API_KEY=your_api_key
     - AZURE_OPENAI_ENDPOINT=your_endpoint
   - Or pass values directly to AIServiceConfig

Example usage:

```python
from src.utils.ai_config import get_default_ai_client
from src.agents.analysis_agent import AnalysisAgent

# Create AI client
ai_client = get_default_ai_client('openai')

# Create agent with AI integration
agent = AnalysisAgent(ai_client=ai_client)

# Process documents with AI
results = await agent.process(input_data)
```
"""
