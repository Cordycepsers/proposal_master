# Organization Research Module Configuration Guide

## Overview

The Organization Research Module provides comprehensive organization profiling, campaign analysis, and social media research capabilities. It integrates with the existing anti-scraping system and supports optional social media API integrations.

## Features

- **Organization Profile Research**: Extract detailed organization information from websites
- **Campaign Analysis**: Research and analyze organization campaigns and initiatives  
- **Social Media Research**: Monitor social media presence and engagement
- **Competitive Intelligence**: Gather market and competitor information
- **Data Export/Import**: Save and load research results in JSON format

## Configuration

### Basic Setup

The module works out-of-the-box with basic functionality:

```python
from src.modules.research import OrganizationResearcher

researcher = OrganizationResearcher()
```

### Anti-Scraping Integration

For enhanced web scraping capabilities, configure the anti-scraping system:

1. Set up API keys in environment variables:
   ```bash
   export CAPTCHA_API_KEY="your_2captcha_key"
   export PROXY_API_KEY="your_proxy_service_key"  # Optional
   ```

2. The module automatically uses the anti-scraping system if available

### Social Media API Integration

For direct social media API access, install optional dependencies and configure:

#### Twitter API (Optional)

1. Install dependency:
   ```bash
   pip install tweepy>=4.14.0
   ```

2. Set up Twitter API credentials:
   ```bash
   export TWITTER_API_KEY="your_api_key"
   export TWITTER_API_SECRET="your_api_secret"
   export TWITTER_ACCESS_TOKEN="your_access_token"
   export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"
   ```

#### Facebook Graph API (Optional)

1. Install dependency:
   ```bash
   pip install facebook-sdk>=3.1.0
   ```

2. Set up Facebook API credentials:
   ```bash
   export FACEBOOK_ACCESS_TOKEN="your_access_token"
   ```

## Usage Examples

### Quick Organization Profile

```python
import asyncio
from src.modules.research import OrganizationResearcher

async def main():
    researcher = OrganizationResearcher()
    
    profile = await researcher.quick_profile_research(
        organization_name="Red Cross",
        website="https://www.redcross.org"
    )
    
    print(f"Organization: {profile.name}")
    print(f"Description: {profile.description}")

asyncio.run(main())
```

### Comprehensive Research

```python
result = await researcher.comprehensive_research(
    organization_name="Doctors Without Borders",
    include_campaigns=True,
    include_social_media=True,
    campaign_keywords=["healthcare", "emergency"],
    social_platforms=["twitter", "facebook"]
)

print(f"Found {len(result.campaigns)} campaigns")
print(f"Social media presence: {len(result.social_media_data)} platforms")
```

### Save and Load Results

```python
from src.modules.research import save_research_result, load_research_result
from pathlib import Path

# Save research results
save_research_result(result, Path("research_output.json"))

# Load research results
loaded_result = load_research_result(Path("research_output.json"))
```

## Data Models

### OrganizationProfile

Core organization information including:
- Basic info (name, website, description)
- Contact details and social media handles
- Leadership and organizational structure
- Focus areas and geographic presence
- Certifications and awards

### CampaignData

Campaign-specific information including:
- Campaign details and timeline
- Financial metrics (target/raised amounts)
- Social media metrics and reach
- Outcomes and success metrics

### SocialMediaMetrics

Social media platform data including:
- Follower counts and engagement rates
- Recent posts and hashtag usage
- Sentiment analysis and mention tracking

## Error Handling

The module includes comprehensive error handling:

- Graceful degradation when optional dependencies are missing
- Fallback to basic functionality when APIs are unavailable
- Detailed logging for troubleshooting
- Confidence scores for data quality assessment

## Integration with Existing Project

The module integrates seamlessly with the existing research infrastructure:

- Uses the same anti-scraping system as `WebResearcher`
- Follows the same logging and configuration patterns
- Compatible with existing database and vector systems
- Exportable through the research module's `__init__.py`

## Performance Considerations

- Implements rate limiting to avoid overwhelming target sites
- Uses asynchronous operations for improved performance
- Supports batch processing for multiple organizations
- Includes caching mechanisms (when anti-scraping system is configured)

## Troubleshooting

### Common Issues

1. **"Anti-scraping system not available"**
   - Expected warning when CAPTCHA API key is not configured
   - Module falls back to basic functionality

2. **"BeautifulSoup not available"**
   - Install: `pip install beautifulsoup4 lxml`

3. **Social media APIs not working**
   - Verify API credentials are set correctly
   - Check API rate limits and quotas

### Logging

Enable debug logging for detailed operation tracking:

```python
import logging
logging.getLogger('src.modules.research.organization_research').setLevel(logging.DEBUG)
```

## Future Enhancements

Planned improvements include:
- LinkedIn API integration
- Enhanced campaign impact analysis
- Machine learning-based sentiment analysis
- Integration with proposal generation system
- Automated competitive landscape mapping
