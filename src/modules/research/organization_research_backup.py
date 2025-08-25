"""
Organization Research Module - Integrated Organization and Campaign Research

This module handles comprehensive organization research and campaign analysis.
Integrates with the existing anti-scraping system and project configuration.
Includes social media research, campaign analysis, and competitive intelligence.

Features:
- Organization profile research and analysis
- Campaign research and impact analysis
- Social media research with API integration
- Competitive intelligence gathering
- Success metrics and benchmarking
- Historical campaign performance analysis
- Stakeholder mapping and influence analysis
"""

import asyncio
import logging
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
from urllib.parse import quote, unquote

# Web scraping libraries (using existing project dependencies)
import requests
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Integration with existing anti-scraping system
try:
    from ...anti_scraping.request_handler import RequestHandler
    from ...anti_scraping.config import AntiScrapingConfig
    ANTI_SCRAPING_AVAILABLE = True
except ImportError:
    ANTI_SCRAPING_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)

# Selenium (optional, controlled by existing project patterns)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Social media API libraries (optional)
try:
    import tweepy  # Twitter API
    TWITTER_API_AVAILABLE = True
except ImportError:
    TWITTER_API_AVAILABLE = False

try:
    import facebook  # Facebook Graph API
    FACEBOOK_API_AVAILABLE = True
except ImportError:
    FACEBOOK_API_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OrganizationProfile:
    """Organization profile structure"""
    name: str
    website: str
    description: str
    sector: str
    headquarters: str
    founded_year: Optional[int]
    size: Optional[str]  # e.g., "1000-5000 employees"
    revenue: Optional[str]
    mission_statement: str
    key_focus_areas: List[str]
    geographic_presence: List[str]
    leadership: List[Dict[str, str]]  # Name, title, bio
    contact_info: Dict[str, str]
    social_media_handles: Dict[str, str]
    recent_news: List[Dict[str, Any]]
    partnerships: List[str]
    awards_recognition: List[Dict[str, Any]]
    financial_info: Dict[str, Any]
    confidence_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class CampaignData:
    """Campaign data structure"""
    campaign_id: str
    title: str
    organization: str
    description: str
    campaign_type: str  # e.g., "awareness", "fundraising", "advocacy"
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    budget: Optional[str]
    target_audience: str
    geographic_scope: List[str]
    channels_used: List[str]  # e.g., "social_media", "tv", "digital"
    key_messages: List[str]
    hashtags: List[str]
    influencers_involved: List[Dict[str, Any]]
    media_coverage: List[Dict[str, Any]]
    success_metrics: Dict[str, Any]
    lessons_learned: List[str]
    assets: List[Dict[str, str]]  # URLs to campaign materials
    source_url: str
    confidence_score: float = 0.0
    discovered_date: datetime = field(default_factory=datetime.now)

@dataclass
class SocialMediaMetrics:
    """Social media metrics structure"""
    platform: str
    handle: str
    followers_count: Optional[int]
    following_count: Optional[int]
    posts_count: Optional[int]
    engagement_rate: Optional[float]
    recent_posts: List[Dict[str, Any]]
    top_hashtags: List[str]
    mention_sentiment: Optional[float]
    growth_trend: Optional[str]  # "increasing", "decreasing", "stable"
    last_post_date: Optional[datetime]
    verification_status: bool = False
    collected_date: datetime = field(default_factory=datetime.now)

@dataclass
class ResearchResult:
    """Complete research result structure"""
    organization_id: str
    organization_profile: OrganizationProfile
    campaigns: List[CampaignData]
    social_media_metrics: List[SocialMediaMetrics]
    competitive_analysis: Dict[str, Any]
    research_summary: str
    recommendations: List[str]
    processing_time: float
    success: bool = True
    error_message: Optional[str] = None

class ResearcherInterface(ABC):
    """Abstract interface for organization researchers"""
    
    @abstractmethod
    async def research_organization(self, organization_name: str, website: Optional[str] = None) -> OrganizationProfile:
        """Research organization profile"""
        pass
    
    @abstractmethod
    async def research_campaigns(self, organization_name: str, keywords: Optional[List[str]] = None) -> List[CampaignData]:
        """Research organization campaigns"""
        pass
    
    @abstractmethod
    def get_researcher_name(self) -> str:
        """Return researcher name"""
        pass

class WebResearcher(ResearcherInterface):
    """Web-based organization researcher using scraping"""
    
    def __init__(self, use_selenium: bool = True):
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    async def research_organization(self, organization_name: str, website: Optional[str] = None) -> OrganizationProfile:
        """Research organization using web scraping"""
        try:
            # If website not provided, search for it
            if not website:
                website = await self._find_organization_website(organization_name)
            
            if not website:
                raise ValueError(f"Could not find website for {organization_name}")
            
            # Scrape organization website
            profile_data = await self._scrape_organization_website(website, organization_name)
            
            # Enhance with additional web research
            enhanced_data = await self._enhance_with_web_search(organization_name, profile_data)
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Web research failed for {organization_name}: {e}")
            return OrganizationProfile(
                name=organization_name,
                website=website or "",
                description="Research failed",
                sector="Unknown",
                headquarters="Unknown",
                founded_year=None,
                size=None,
                revenue=None,
                mission_statement="",
                key_focus_areas=[],
                geographic_presence=[],
                leadership=[],
                contact_info={},
                social_media_handles={},
                recent_news=[],
                partnerships=[],
                awards_recognition=[],
                financial_info={},
                confidence_score=0.0
            )
    
    async def _find_organization_website(self, organization_name: str) -> Optional[str]:
        """Find organization website using search"""
        try:
            search_query = f"{organization_name} official website"
            search_url = f"https://www.google.com/search?q={quote(search_query)}"
            
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for first search result link
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/url?q='):
                    url = href.split('/url?q=')[1].split('&')[0]
                    if url.startswith('http') and not 'google.com' in url:
                        return unquote(url)
            
            return None
            
        except Exception as e:
            logger.warning(f"Website search failed for {organization_name}: {e}")
            return None
    
    async def _scrape_organization_website(self, website: str, organization_name: str) -> OrganizationProfile:
        """Scrape organization website for profile information"""
        try:
            response = self.session.get(website, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            title = soup.find('title')
            title_text = title.get_text() if title else organization_name
            
            # Extract description from meta tags
            description_meta = soup.find('meta', attrs={'name': 'description'})
            description = description_meta.get('content', '') if description_meta else ""
            
            # Extract mission statement (look for common patterns)
            mission_patterns = [
                'mission', 'about us', 'our mission', 'what we do',
                'purpose', 'vision', 'our story'
            ]
            mission_statement = self._extract_mission_statement(soup, mission_patterns)
            
            # Extract contact information
            contact_info = self._extract_contact_info(soup)
            
            # Extract social media handles
            social_media = self._extract_social_media_handles(soup)
            
            # Extract leadership information
            leadership = self._extract_leadership_info(soup)
            
            # Extract focus areas from content
            focus_areas = self._extract_focus_areas(soup)
            
            return OrganizationProfile(
                name=organization_name,
                website=website,
                description=description or self._extract_description_from_content(soup),
                sector=self._determine_sector(soup, description),
                headquarters=self._extract_headquarters(soup),
                founded_year=self._extract_founded_year(soup),
                size=None,  # Difficult to extract from website
                revenue=None,  # Usually not public
                mission_statement=mission_statement,
                key_focus_areas=focus_areas,
                geographic_presence=self._extract_geographic_presence(soup),
                leadership=leadership,
                contact_info=contact_info,
                social_media_handles=social_media,
                recent_news=[],  # Would need separate news scraping
                partnerships=self._extract_partnerships(soup),
                awards_recognition=[],  # Would need separate research
                financial_info={},
                confidence_score=0.7  # Web scraping has moderate confidence
            )
            
        except Exception as e:
            logger.error(f"Website scraping failed for {website}: {e}")
            raise
    
    def _extract_mission_statement(self, soup: BeautifulSoup, patterns: List[str]) -> str:
        """Extract mission statement from website"""
        for pattern in patterns:
            # Look for headings containing mission-related keywords
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4'], string=re.compile(pattern, re.IGNORECASE)):
                # Get the next paragraph or div
                next_element = heading.find_next(['p', 'div'])
                if next_element:
                    text = next_element.get_text(strip=True)
                    if len(text) > 50:  # Reasonable mission statement length
                        return text[:500]  # Limit length
        
        # Fallback: look for about section
        about_section = soup.find('section', id=re.compile('about', re.IGNORECASE))
        if about_section:
            paragraphs = about_section.find_all('p')
            if paragraphs:
                return paragraphs[0].get_text(strip=True)[:500]
        
        return ""
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract contact information"""
        contact_info = {}
        
        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, soup.get_text())
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone patterns
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, soup.get_text())
        if phones:
            contact_info['phone'] = phones[0]
        
        # Address (simplified extraction)
        address_keywords = ['address', 'location', 'office']
        for keyword in address_keywords:
            element = soup.find(string=re.compile(keyword, re.IGNORECASE))
            if element:
                parent = element.parent
                if parent:
                    address_text = parent.get_text(strip=True)
                    if len(address_text) > 20:
                        contact_info['address'] = address_text[:200]
                        break
        
        return contact_info
    
    def _extract_social_media_handles(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media handles"""
        social_media = {}
        
        # Social media patterns
        social_patterns = {
            'twitter': r'twitter\.com/([A-Za-z0-9_]+)',
            'facebook': r'facebook\.com/([A-Za-z0-9._]+)',
            'linkedin': r'linkedin\.com/(?:company|in)/([A-Za-z0-9-]+)',
            'instagram': r'instagram\.com/([A-Za-z0-9_.]+)',
            'youtube': r'youtube\.com/(?:channel/|user/|c/)([A-Za-z0-9_-]+)'
        }
        
        page_text = soup.get_text()
        for link in soup.find_all('a', href=True):
            href = link['href']
            for platform, pattern in social_patterns.items():
                match = re.search(pattern, href)
                if match:
                    social_media[platform] = match.group(1)
        
        return social_media
    
    def _extract_leadership_info(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract leadership information"""
        leadership = []
        
        # Look for team/leadership sections
        leadership_keywords = ['team', 'leadership', 'staff', 'board', 'directors']
        
        for keyword in leadership_keywords:
            section = soup.find(['section', 'div'], id=re.compile(keyword, re.IGNORECASE))
            if not section:
                section = soup.find(['section', 'div'], class_=re.compile(keyword, re.IGNORECASE))
            
            if section:
                # Look for person cards/profiles
                person_elements = section.find_all(['div', 'article'], class_=re.compile('person|member|profile', re.IGNORECASE))
                
                for person in person_elements[:5]:  # Limit to top 5
                    name_elem = person.find(['h3', 'h4', 'h5'])
                    title_elem = person.find(['p', 'span'], class_=re.compile('title|position|role', re.IGNORECASE))
                    
                    if name_elem:
                        person_data = {
                            'name': name_elem.get_text(strip=True),
                            'title': title_elem.get_text(strip=True) if title_elem else "",
                            'bio': ""
                        }
                        leadership.append(person_data)
                
                if leadership:
                    break
        
        return leadership
    
    def _extract_focus_areas(self, soup: BeautifulSoup) -> List[str]:
        """Extract key focus areas"""
        focus_areas = []
        
        # Common focus area keywords
        focus_keywords = [
            'climate', 'environment', 'sustainability', 'health', 'education',
            'poverty', 'human rights', 'democracy', 'development', 'humanitarian',
            'peace', 'security', 'gender', 'youth', 'children', 'refugees'
        ]
        
        page_text = soup.get_text().lower()
        
        for keyword in focus_keywords:
            if keyword in page_text:
                # Count occurrences to determine relevance
                count = page_text.count(keyword)
                if count >= 3:  # Appears multiple times
                    focus_areas.append(keyword.title())
        
        return focus_areas[:10]  # Limit to top 10
    
    def _extract_description_from_content(self, soup: BeautifulSoup) -> str:
        """Extract description from page content"""
        # Look for first substantial paragraph
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 100:  # Substantial content
                return text[:300]  # Limit length
        return ""
    
    def _determine_sector(self, soup: BeautifulSoup, description: str) -> str:
        """Determine organization sector"""
        sector_keywords = {
            'Non-profit': ['nonprofit', 'non-profit', 'ngo', 'charity', 'foundation'],
            'Government': ['government', 'ministry', 'department', 'agency', 'public'],
            'International': ['united nations', 'un ', 'world bank', 'international'],
            'Corporate': ['company', 'corporation', 'inc', 'ltd', 'llc'],
            'Academic': ['university', 'college', 'research', 'institute', 'academic']
        }
        
        content = (soup.get_text() + " " + description).lower()
        
        for sector, keywords in sector_keywords.items():
            if any(keyword in content for keyword in keywords):
                return sector
        
        return "Unknown"
    
    def _extract_headquarters(self, soup: BeautifulSoup) -> str:
        """Extract headquarters location"""
        location_patterns = [
            r'headquarter[s]?\s+(?:in|at)?\s+([A-Za-z\s,]+)',
            r'based\s+in\s+([A-Za-z\s,]+)',
            r'located\s+in\s+([A-Za-z\s,]+)'
        ]
        
        content = soup.get_text()
        
        for pattern in location_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if len(location) < 50:  # Reasonable location length
                    return location
        
        return "Unknown"
    
    def _extract_founded_year(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract founding year"""
        year_patterns = [
            r'founded\s+in\s+(\d{4})',
            r'established\s+in\s+(\d{4})',
            r'since\s+(\d{4})',
            r'created\s+in\s+(\d{4})'
        ]
        
        content = soup.get_text()
        
        for pattern in year_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                if 1800 <= year <= datetime.now().year:  # Reasonable year range
                    return year
        
        return None
    
    def _extract_geographic_presence(self, soup: BeautifulSoup) -> List[str]:
        """Extract geographic presence"""
        # Common country/region names
        locations = [
            'United States', 'United Kingdom', 'Canada', 'Australia', 'Germany',
            'France', 'Italy', 'Spain', 'Netherlands', 'Sweden', 'Norway',
            'Kenya', 'Nigeria', 'South Africa', 'Ghana', 'Ethiopia',
            'India', 'China', 'Japan', 'Brazil', 'Mexico', 'Argentina',
            'Africa', 'Asia', 'Europe', 'Americas', 'Middle East'
        ]
        
        content = soup.get_text()
        found_locations = []
        
        for location in locations:
            if location.lower() in content.lower():
                found_locations.append(location)
        
        return found_locations[:10]  # Limit results
    
    def _extract_partnerships(self, soup: BeautifulSoup) -> List[str]:
        """Extract partnerships"""
        partnership_keywords = ['partner', 'collaboration', 'alliance', 'network']
        partnerships = []
        
        for keyword in partnership_keywords:
            # Look for sections mentioning partnerships
            elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
            for element in elements[:3]:  # Limit search
                parent = element.parent
                if parent:
                    text = parent.get_text(strip=True)
                    # Extract organization names (simplified)
                    words = text.split()
                    for i, word in enumerate(words):
                        if word.lower() == keyword.lower() and i < len(words) - 1:
                            # Get next few words as potential partner name
                            partner = ' '.join(words[i+1:i+4])
                            if len(partner) > 5:
                                partnerships.append(partner)
        
        return partnerships[:5]  # Limit results
    
    async def _enhance_with_web_search(self, organization_name: str, profile: OrganizationProfile) -> OrganizationProfile:
        """Enhance profile with additional web search"""
        try:
            # Search for recent news
            news_results = await self._search_organization_news(organization_name)
            profile.recent_news = news_results
            
            # Search for awards and recognition
            awards_results = await self._search_organization_awards(organization_name)
            profile.awards_recognition = awards_results
            
            # Increase confidence score for enhanced data
            profile.confidence_score = min(0.9, profile.confidence_score + 0.2)
            
        except Exception as e:
            logger.warning(f"Enhancement failed for {organization_name}: {e}")
        
        return profile
    
    async def _search_organization_news(self, organization_name: str) -> List[Dict[str, Any]]:
        """Search for recent news about organization"""
        try:
            search_query = f"{organization_name} news recent"
            search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}&tbm=nws"
            
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_results = []
            # Parse news results (simplified)
            for result in soup.find_all('div', class_='g')[:5]:
                title_elem = result.find('h3')
                link_elem = result.find('a', href=True)
                
                if title_elem and link_elem:
                    news_results.append({
                        'title': title_elem.get_text(strip=True),
                        'url': link_elem['href'],
                        'date': datetime.now().isoformat(),  # Would need better date extraction
                        'source': 'Google News'
                    })
            
            return news_results
            
        except Exception as e:
            logger.warning(f"News search failed for {organization_name}: {e}")
            return []
    
    async def _search_organization_awards(self, organization_name: str) -> List[Dict[str, Any]]:
        """Search for awards and recognition"""
        try:
            search_query = f"{organization_name} awards recognition achievements"
            search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
            
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            awards = []
            # Look for award-related content (simplified)
            award_keywords = ['award', 'recognition', 'prize', 'honor', 'achievement']
            
            for result in soup.find_all('div', class_='g')[:3]:
                text = result.get_text().lower()
                for keyword in award_keywords:
                    if keyword in text:
                        title_elem = result.find('h3')
                        if title_elem:
                            awards.append({
                                'title': title_elem.get_text(strip=True),
                                'year': None,  # Would need better extraction
                                'description': text[:200],
                                'source': 'Web Search'
                            })
                            break
            
            return awards
            
        except Exception as e:
            logger.warning(f"Awards search failed for {organization_name}: {e}")
            return []
    
    async def research_campaigns(self, organization_name: str, keywords: Optional[List[str]] = None) -> List[CampaignData]:
        """Research organization campaigns"""
        campaigns = []
        
        try:
            # Search for campaigns using various sources
            search_terms = [organization_name]
            if keywords:
                search_terms.extend(keywords)
            
            # Search for campaign information
            for term in search_terms[:3]:  # Limit searches
                campaign_results = await self._search_campaigns(term, organization_name)
                campaigns.extend(campaign_results)
            
            # Deduplicate campaigns
            unique_campaigns = self._deduplicate_campaigns(campaigns)
            
            return unique_campaigns[:10]  # Limit results
            
        except Exception as e:
            logger.error(f"Campaign research failed for {organization_name}: {e}")
            return []
    
    async def _search_campaigns(self, search_term: str, organization_name: str) -> List[CampaignData]:
        """Search for campaigns using web search"""
        try:
            search_query = f"{search_term} campaign marketing advertising"
            search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
            
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            campaigns = []
            
            for result in soup.find_all('div', class_='g')[:5]:
                title_elem = result.find('h3')
                link_elem = result.find('a', href=True)
                snippet_elem = result.find('span', class_='st')
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    url = link_elem['href']
                    description = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    # Check if this looks like a campaign
                    campaign_keywords = ['campaign', 'initiative', 'program', 'project', 'movement']
                    if any(keyword in title.lower() or keyword in description.lower() for keyword in campaign_keywords):
                        campaign_id = hashlib.md5(url.encode()).hexdigest()[:8]
                        
                        campaign = CampaignData(
                            campaign_id=campaign_id,
                            title=title,
                            organization=organization_name,
                            description=description,
                            campaign_type=self._determine_campaign_type(title, description),
                            start_date=None,
                            end_date=None,
                            budget=None,
                            target_audience="Unknown",
                            geographic_scope=[],
                            channels_used=self._extract_channels_from_text(description),
                            key_messages=[],
                            hashtags=self._extract_hashtags_from_text(description),
                            influencers_involved=[],
                            media_coverage=[],
                            success_metrics={},
                            lessons_learned=[],
                            assets=[],
                            source_url=url,
                            confidence_score=0.6
                        )
                        
                        campaigns.append(campaign)
            
            return campaigns
            
        except Exception as e:
            logger.warning(f"Campaign search failed for {search_term}: {e}")
            return []
    
    def _determine_campaign_type(self, title: str, description: str) -> str:
        """Determine campaign type from title and description"""
        text = (title + " " + description).lower()
        
        type_keywords = {
            'awareness': ['awareness', 'education', 'inform', 'knowledge'],
            'fundraising': ['fundraising', 'donate', 'donation', 'fund', 'money'],
            'advocacy': ['advocacy', 'policy', 'change', 'action', 'petition'],
            'recruitment': ['recruitment', 'hiring', 'jobs', 'careers', 'volunteer'],
            'product': ['product', 'launch', 'new', 'service', 'offering']
        }
        
        for campaign_type, keywords in type_keywords.items():
            if any(keyword in text for keyword in keywords):
                return campaign_type
        
        return "general"
    
    def _extract_channels_from_text(self, text: str) -> List[str]:
        """Extract marketing channels from text"""
        channels = []
        channel_keywords = {
            'social_media': ['social media', 'facebook', 'twitter', 'instagram', 'linkedin'],
            'digital': ['digital', 'online', 'web', 'internet'],
            'tv': ['television', 'tv', 'broadcast'],
            'radio': ['radio', 'podcast'],
            'print': ['print', 'newspaper', 'magazine'],
            'outdoor': ['billboard', 'outdoor', 'poster'],
            'email': ['email', 'newsletter']
        }
        
        text_lower = text.lower()
        for channel, keywords in channel_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                channels.append(channel)
        
        return channels
    
    def _extract_hashtags_from_text(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text)
        return hashtags[:5]  # Limit results
    
    def _deduplicate_campaigns(self, campaigns: List[CampaignData]) -> List[CampaignData]:
        """Remove duplicate campaigns"""
        seen_urls = set()
        unique_campaigns = []
        
        for campaign in campaigns:
            if campaign.source_url not in seen_urls:
                seen_urls.add(campaign.source_url)
                unique_campaigns.append(campaign)
        
        return unique_campaigns
    
    def get_researcher_name(self) -> str:
        return "Web Researcher"

class SocialMediaResearcher(ResearcherInterface):
    """Social media researcher using APIs and scraping"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        
        # Initialize Twitter API if available
        self.twitter_api = None
        if TWITTER_API_AVAILABLE and 'twitter' in self.api_keys:
            try:
                auth = tweepy.OAuthHandler(
                    self.api_keys['twitter']['consumer_key'],
                    self.api_keys['twitter']['consumer_secret']
                )
                auth.set_access_token(
                    self.api_keys['twitter']['access_token'],
                    self.api_keys['twitter']['access_token_secret']
                )
                self.twitter_api = tweepy.API(auth, wait_on_rate_limit=True)
            except Exception as e:
                logger.warning(f"Twitter API initialization failed: {e}")
        
        # Initialize Facebook API if available
        self.facebook_api = None
        if FACEBOOK_API_AVAILABLE and 'facebook' in self.api_keys:
            try:
                self.facebook_api = facebook.GraphAPI(access_token=self.api_keys['facebook']['access_token'])
            except Exception as e:
                logger.warning(f"Facebook API initialization failed: {e}")
    
    async def research_organization(self, organization_name: str, website: Optional[str] = None) -> OrganizationProfile:
        """Research organization using social media"""
        try:
            # Get social media metrics
            social_metrics = await self.get_social_media_metrics(organization_name)
            
            # Create basic profile from social media data
            profile = OrganizationProfile(
                name=organization_name,
                website=website or "",
                description=self._extract_description_from_social(social_metrics),
                sector="Unknown",
                headquarters="Unknown",
                founded_year=None,
                size=None,
                revenue=None,
                mission_statement="",
                key_focus_areas=self._extract_focus_areas_from_social(social_metrics),
                geographic_presence=[],
                leadership=[],
                contact_info={},
                social_media_handles=self._extract_handles_from_metrics(social_metrics),
                recent_news=[],
                partnerships=[],
                awards_recognition=[],
                financial_info={},
                confidence_score=0.5  # Social media has moderate confidence
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Social media research failed for {organization_name}: {e}")
            raise
    
    async def research_campaigns(self, organization_name: str, keywords: Optional[List[str]] = None) -> List[CampaignData]:
        """Research campaigns using social media"""
        campaigns = []
        
        try:
            # Search for campaign-related posts
            search_terms = [f"{organization_name} campaign"]
            if keywords:
                search_terms.extend([f"{organization_name} {kw}" for kw in keywords])
            
            for term in search_terms[:3]:
                campaign_posts = await self._search_campaign_posts(term)
                campaigns.extend(self._convert_posts_to_campaigns(campaign_posts, organization_name))
            
            return campaigns[:10]  # Limit results
            
        except Exception as e:
            logger.error(f"Social media campaign research failed for {organization_name}: {e}")
            return []
    
    async def get_social_media_metrics(self, organization_name: str) -> List[SocialMediaMetrics]:
        """Get social media metrics for organization"""
        metrics = []
        
        # Twitter metrics
        if self.twitter_api:
            twitter_metrics = await self._get_twitter_metrics(organization_name)
            if twitter_metrics:
                metrics.append(twitter_metrics)
        
        # Facebook metrics
        if self.facebook_api:
            facebook_metrics = await self._get_facebook_metrics(organization_name)
            if facebook_metrics:
                metrics.append(facebook_metrics)
        
        # Fallback to web scraping for public data
        if not metrics:
            scraped_metrics = await self._scrape_social_media_metrics(organization_name)
            metrics.extend(scraped_metrics)
        
        return metrics
    
    async def _get_twitter_metrics(self, organization_name: str) -> Optional[SocialMediaMetrics]:
        """Get Twitter metrics using API"""
        try:
            # Search for organization's Twitter account
            users = self.twitter_api.search_users(organization_name, count=1)
            if not users:
                return None
            
            user = users[0]
            
            # Get recent tweets
            tweets = self.twitter_api.user_timeline(user.id, count=10, tweet_mode='extended')
            recent_posts = []
            
            for tweet in tweets:
                recent_posts.append({
                    'id': tweet.id_str,
                    'text': tweet.full_text,
                    'created_at': tweet.created_at.isoformat(),
                    'retweets': tweet.retweet_count,
                    'likes': tweet.favorite_count,
                    'replies': tweet.reply_count if hasattr(tweet, 'reply_count') else 0
                })
            
            # Calculate engagement rate
            total_engagement = sum(post['retweets'] + post['likes'] + post['replies'] for post in recent_posts)
            engagement_rate = (total_engagement / (len(recent_posts) * user.followers_count)) * 100 if user.followers_count > 0 else 0
            
            return SocialMediaMetrics(
                platform="Twitter",
                handle=user.screen_name,
                followers_count=user.followers_count,
                following_count=user.friends_count,
                posts_count=user.statuses_count,
                engagement_rate=engagement_rate,
                recent_posts=recent_posts,
                top_hashtags=self._extract_top_hashtags(recent_posts),
                mention_sentiment=None,  # Would need sentiment analysis
                growth_trend="stable",  # Would need historical data
                last_post_date=tweets[0].created_at if tweets else None,
                verification_status=user.verified
            )
            
        except Exception as e:
            logger.warning(f"Twitter metrics failed for {organization_name}: {e}")
            return None
    
    async def _get_facebook_metrics(self, organization_name: str) -> Optional[SocialMediaMetrics]:
        """Get Facebook metrics using API"""
        try:
            # Facebook API requires page ID, which is difficult to get from name
            # This is a simplified implementation
            
            # Search for page (requires specific permissions)
            search_results = self.facebook_api.search(
                type='page',
                q=organization_name,
                fields='id,name,fan_count,talking_about_count'
            )
            
            if not search_results.get('data'):
                return None
            
            page = search_results['data'][0]
            
            # Get recent posts
            posts = self.facebook_api.get_connections(
                page['id'],
                'posts',
                fields='message,created_time,likes.summary(true),comments.summary(true),shares'
            )
            
            recent_posts = []
            for post in posts.get('data', [])[:10]:
                recent_posts.append({
                    'id': post['id'],
                    'text': post.get('message', ''),
                    'created_at': post['created_time'],
                    'likes': post.get('likes', {}).get('summary', {}).get('total_count', 0),
                    'comments': post.get('comments', {}).get('summary', {}).get('total_count', 0),
                    'shares': post.get('shares', {}).get('count', 0)
                })
            
            return SocialMediaMetrics(
                platform="Facebook",
                handle=page['name'],
                followers_count=page.get('fan_count'),
                following_count=None,
                posts_count=None,
                engagement_rate=None,  # Would need calculation
                recent_posts=recent_posts,
                top_hashtags=[],
                mention_sentiment=None,
                growth_trend="stable",
                last_post_date=None,
                verification_status=False
            )
            
        except Exception as e:
            logger.warning(f"Facebook metrics failed for {organization_name}: {e}")
            return None
    
    async def _scrape_social_media_metrics(self, organization_name: str) -> List[SocialMediaMetrics]:
        """Scrape social media metrics from public pages"""
        metrics = []
        
        if not SELENIUM_AVAILABLE:
            return metrics
        
        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Scrape Twitter (if accessible)
            twitter_handle = await self._find_twitter_handle(organization_name)
            if twitter_handle:
                twitter_metrics = await self._scrape_twitter_metrics(driver, twitter_handle)
                if twitter_metrics:
                    metrics.append(twitter_metrics)
            
            driver.quit()
            
        except Exception as e:
            logger.warning(f"Social media scraping failed for {organization_name}: {e}")
        
        return metrics
    
    async def _find_twitter_handle(self, organization_name: str) -> Optional[str]:
        """Find Twitter handle for organization"""
        try:
            search_query = f"{organization_name} twitter"
            search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
            
            session = requests.Session()
            response = session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for Twitter links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'twitter.com/' in href:
                    match = re.search(r'twitter\.com/([A-Za-z0-9_]+)', href)
                    if match:
                        return match.group(1)
            
            return None
            
        except Exception as e:
            logger.warning(f"Twitter handle search failed for {organization_name}: {e}")
            return None
    
    async def _scrape_twitter_metrics(self, driver, handle: str) -> Optional[SocialMediaMetrics]:
        """Scrape Twitter metrics using Selenium"""
        try:
            url = f"https://twitter.com/{handle}"
            driver.get(url)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Extract metrics (simplified - Twitter's structure changes frequently)
            followers_elem = driver.find_element(By.XPATH, "//a[contains(@href, '/followers')]//span")
            following_elem = driver.find_element(By.XPATH, "//a[contains(@href, '/following')]//span")
            
            followers_text = followers_elem.text if followers_elem else "0"
            following_text = following_elem.text if following_elem else "0"
            
            # Convert text to numbers (handle K, M suffixes)
            followers_count = self._parse_social_number(followers_text)
            following_count = self._parse_social_number(following_text)
            
            return SocialMediaMetrics(
                platform="Twitter",
                handle=handle,
                followers_count=followers_count,
                following_count=following_count,
                posts_count=None,
                engagement_rate=None,
                recent_posts=[],
                top_hashtags=[],
                mention_sentiment=None,
                growth_trend="unknown",
                last_post_date=None,
                verification_status=False
            )
            
        except Exception as e:
            logger.warning(f"Twitter scraping failed for {handle}: {e}")
            return None
    
    def _parse_social_number(self, text: str) -> Optional[int]:
        """Parse social media numbers (e.g., '1.2K' -> 1200)"""
        try:
            text = text.replace(',', '').strip()
            
            if text.endswith('K'):
                return int(float(text[:-1]) * 1000)
            elif text.endswith('M'):
                return int(float(text[:-1]) * 1000000)
            elif text.endswith('B'):
                return int(float(text[:-1]) * 1000000000)
            else:
                return int(text)
        except:
            return None
    
    async def _search_campaign_posts(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for campaign-related posts"""
        posts = []
        
        # Twitter search
        if self.twitter_api:
            try:
                tweets = self.twitter_api.search_tweets(q=search_term, count=20, tweet_mode='extended')
                for tweet in tweets:
                    posts.append({
                        'platform': 'Twitter',
                        'id': tweet.id_str,
                        'text': tweet.full_text,
                        'author': tweet.user.screen_name,
                        'created_at': tweet.created_at.isoformat(),
                        'engagement': tweet.retweet_count + tweet.favorite_count,
                        'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}"
                    })
            except Exception as e:
                logger.warning(f"Twitter search failed for {search_term}: {e}")
        
        return posts
    
    def _convert_posts_to_campaigns(self, posts: List[Dict[str, Any]], organization_name: str) -> List[CampaignData]:
        """Convert social media posts to campaign data"""
        campaigns = []
        
        # Group posts by potential campaigns (simplified)
        campaign_posts = {}
        
        for post in posts:
            # Extract potential campaign hashtags
            hashtags = re.findall(r'#\w+', post['text'])
            
            for hashtag in hashtags:
                if hashtag not in campaign_posts:
                    campaign_posts[hashtag] = []
                campaign_posts[hashtag].append(post)
        
        # Create campaign data from grouped posts
        for hashtag, related_posts in campaign_posts.items():
            if len(related_posts) >= 2:  # At least 2 posts to consider it a campaign
                campaign_id = hashlib.md5(f"{organization_name}_{hashtag}".encode()).hexdigest()[:8]
                
                # Aggregate data from posts
                total_engagement = sum(post['engagement'] for post in related_posts)
                earliest_post = min(related_posts, key=lambda x: x['created_at'])
                latest_post = max(related_posts, key=lambda x: x['created_at'])
                
                campaign = CampaignData(
                    campaign_id=campaign_id,
                    title=f"{hashtag} Campaign",
                    organization=organization_name,
                    description=f"Social media campaign using {hashtag}",
                    campaign_type="social_media",
                    start_date=datetime.fromisoformat(earliest_post['created_at'].replace('Z', '+00:00')),
                    end_date=datetime.fromisoformat(latest_post['created_at'].replace('Z', '+00:00')),
                    budget=None,
                    target_audience="Social media users",
                    geographic_scope=[],
                    channels_used=["social_media"],
                    key_messages=[],
                    hashtags=[hashtag],
                    influencers_involved=[],
                    media_coverage=[],
                    success_metrics={
                        'total_posts': len(related_posts),
                        'total_engagement': total_engagement,
                        'platforms': list(set(post['platform'] for post in related_posts))
                    },
                    lessons_learned=[],
                    assets=[{'type': 'social_posts', 'urls': [post['url'] for post in related_posts]}],
                    source_url=related_posts[0]['url'],
                    confidence_score=0.7
                )
                
                campaigns.append(campaign)
        
        return campaigns
    
    def _extract_description_from_social(self, metrics: List[SocialMediaMetrics]) -> str:
        """Extract description from social media data"""
        if not metrics:
            return ""
        
        # Use bio or recent posts to create description
        for metric in metrics:
            if metric.recent_posts:
                # Use first substantial post as description
                for post in metric.recent_posts:
                    text = post.get('text', '')
                    if len(text) > 50:
                        return text[:200]
        
        return ""
    
    def _extract_focus_areas_from_social(self, metrics: List[SocialMediaMetrics]) -> List[str]:
        """Extract focus areas from social media content"""
        focus_areas = []
        
        # Common focus area keywords
        focus_keywords = [
            'climate', 'environment', 'sustainability', 'health', 'education',
            'poverty', 'human rights', 'democracy', 'development', 'humanitarian'
        ]
        
        all_text = ""
        for metric in metrics:
            for post in metric.recent_posts:
                all_text += " " + post.get('text', '')
        
        all_text = all_text.lower()
        
        for keyword in focus_keywords:
            if keyword in all_text:
                focus_areas.append(keyword.title())
        
        return focus_areas[:5]
    
    def _extract_handles_from_metrics(self, metrics: List[SocialMediaMetrics]) -> Dict[str, str]:
        """Extract social media handles from metrics"""
        handles = {}
        for metric in metrics:
            handles[metric.platform.lower()] = metric.handle
        return handles
    
    def _extract_top_hashtags(self, posts: List[Dict[str, Any]]) -> List[str]:
        """Extract top hashtags from posts"""
        hashtag_counts = {}
        
        for post in posts:
            hashtags = re.findall(r'#\w+', post.get('text', ''))
            for hashtag in hashtags:
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        
        # Sort by frequency and return top hashtags
        sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
        return [hashtag for hashtag, count in sorted_hashtags[:10]]
    
    def get_researcher_name(self) -> str:
        return "Social Media Researcher"

class OrganizationResearchModule:
    """Main Organization Research Module - Orchestrates all researchers"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize researchers
        self.researchers = {}
        
        # Web researcher (always available)
        self.researchers['web'] = WebResearcher(use_selenium=self.config.get('use_selenium', True))
        
        # Social media researcher (if API keys provided)
        api_keys = self.config.get('social_media_api_keys', {})
        if api_keys:
            self.researchers['social_media'] = SocialMediaResearcher(api_keys)
        
        # Set primary researcher
        primary_researcher_name = self.config.get('primary_researcher', 'web')
        self.primary_researcher = self.researchers.get(primary_researcher_name, self.researchers['web'])
        
        # Configuration
        self.max_concurrent_research = self.config.get('max_concurrent_research', 3)
        self.enable_comprehensive_research = self.config.get('enable_comprehensive_research', True)
        
        logger.info(f"Organization Research Module initialized with {len(self.researchers)} researchers")
        logger.info(f"Primary researcher: {self.primary_researcher.get_researcher_name()}")
    
    async def research_organization_comprehensive(self, organization_name: str, website: Optional[str] = None) -> ResearchResult:
        """Comprehensive organization research using all available researchers"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Research organization profile
            profile_tasks = []
            for name, researcher in self.researchers.items():
                task = asyncio.create_task(
                    researcher.research_organization(organization_name, website),
                    name=f"profile_{name}"
                )
                profile_tasks.append(task)
            
            # Research campaigns
            campaign_tasks = []
            for name, researcher in self.researchers.items():
                task = asyncio.create_task(
                    researcher.research_campaigns(organization_name),
                    name=f"campaigns_{name}"
                )
                campaign_tasks.append(task)
            
            # Execute all tasks concurrently
            all_tasks = profile_tasks + campaign_tasks
            results = await asyncio.gather(*all_tasks, return_exceptions=True)
            
            # Process results
            profiles = []
            all_campaigns = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"Task {all_tasks[i].get_name()} failed: {result}")
                    continue
                
                if i < len(profile_tasks):  # Profile result
                    if isinstance(result, OrganizationProfile):
                        profiles.append(result)
                else:  # Campaign result
                    if isinstance(result, list):
                        all_campaigns.extend(result)
            
            # Merge profiles
            merged_profile = self._merge_organization_profiles(profiles, organization_name)
            
            # Deduplicate campaigns
            unique_campaigns = self._deduplicate_campaigns(all_campaigns)
            
            # Get social media metrics
            social_metrics = []
            if 'social_media' in self.researchers:
                try:
                    social_metrics = await self.researchers['social_media'].get_social_media_metrics(organization_name)
                except Exception as e:
                    logger.warning(f"Social media metrics failed: {e}")
            
            # Generate competitive analysis
            competitive_analysis = await self._generate_competitive_analysis(organization_name, merged_profile)
            
            # Generate summary and recommendations
            research_summary = self._generate_research_summary(merged_profile, unique_campaigns, social_metrics)
            recommendations = self._generate_recommendations(merged_profile, unique_campaigns, social_metrics)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ResearchResult(
                organization_id=hashlib.md5(organization_name.encode()).hexdigest()[:8],
                organization_profile=merged_profile,
                campaigns=unique_campaigns,
                social_media_metrics=social_metrics,
                competitive_analysis=competitive_analysis,
                research_summary=research_summary,
                recommendations=recommendations,
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Comprehensive research failed for {organization_name}: {e}")
            return ResearchResult(
                organization_id=hashlib.md5(organization_name.encode()).hexdigest()[:8],
                organization_profile=OrganizationProfile(
                    name=organization_name,
                    website=website or "",
                    description="Research failed",
                    sector="Unknown",
                    headquarters="Unknown",
                    founded_year=None,
                    size=None,
                    revenue=None,
                    mission_statement="",
                    key_focus_areas=[],
                    geographic_presence=[],
                    leadership=[],
                    contact_info={},
                    social_media_handles={},
                    recent_news=[],
                    partnerships=[],
                    awards_recognition=[],
                    financial_info={}
                ),
                campaigns=[],
                social_media_metrics=[],
                competitive_analysis={},
                research_summary=f"Research failed: {str(e)}",
                recommendations=[],
                processing_time=asyncio.get_event_loop().time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    def _merge_organization_profiles(self, profiles: List[OrganizationProfile], organization_name: str) -> OrganizationProfile:
        """Merge multiple organization profiles into one comprehensive profile"""
        if not profiles:
            return OrganizationProfile(
                name=organization_name,
                website="",
                description="No data available",
                sector="Unknown",
                headquarters="Unknown",
                founded_year=None,
                size=None,
                revenue=None,
                mission_statement="",
                key_focus_areas=[],
                geographic_presence=[],
                leadership=[],
                contact_info={},
                social_media_handles={},
                recent_news=[],
                partnerships=[],
                awards_recognition=[],
                financial_info={}
            )
        
        # Start with the profile with highest confidence
        base_profile = max(profiles, key=lambda p: p.confidence_score)
        
        # Merge data from other profiles
        for profile in profiles:
            if profile == base_profile:
                continue
            
            # Merge lists (remove duplicates)
            base_profile.key_focus_areas = list(set(base_profile.key_focus_areas + profile.key_focus_areas))
            base_profile.geographic_presence = list(set(base_profile.geographic_presence + profile.geographic_presence))
            base_profile.partnerships = list(set(base_profile.partnerships + profile.partnerships))
            
            # Merge leadership (avoid duplicates by name)
            existing_names = {leader.get('name', '').lower() for leader in base_profile.leadership}
            for leader in profile.leadership:
                if leader.get('name', '').lower() not in existing_names:
                    base_profile.leadership.append(leader)
            
            # Merge contact info
            base_profile.contact_info.update(profile.contact_info)
            
            # Merge social media handles
            base_profile.social_media_handles.update(profile.social_media_handles)
            
            # Merge news and awards
            base_profile.recent_news.extend(profile.recent_news)
            base_profile.awards_recognition.extend(profile.awards_recognition)
            
            # Use better description if available
            if len(profile.description) > len(base_profile.description):
                base_profile.description = profile.description
            
            # Use better mission statement if available
            if len(profile.mission_statement) > len(base_profile.mission_statement):
                base_profile.mission_statement = profile.mission_statement
            
            # Fill in missing basic info
            if not base_profile.website and profile.website:
                base_profile.website = profile.website
            if base_profile.sector == "Unknown" and profile.sector != "Unknown":
                base_profile.sector = profile.sector
            if base_profile.headquarters == "Unknown" and profile.headquarters != "Unknown":
                base_profile.headquarters = profile.headquarters
            if not base_profile.founded_year and profile.founded_year:
                base_profile.founded_year = profile.founded_year
        
        # Calculate merged confidence score
        base_profile.confidence_score = min(0.95, sum(p.confidence_score for p in profiles) / len(profiles) + 0.1)
        
        # Limit list sizes
        base_profile.key_focus_areas = base_profile.key_focus_areas[:10]
        base_profile.geographic_presence = base_profile.geographic_presence[:15]
        base_profile.leadership = base_profile.leadership[:10]
        base_profile.recent_news = base_profile.recent_news[:20]
        base_profile.awards_recognition = base_profile.awards_recognition[:10]
        base_profile.partnerships = base_profile.partnerships[:15]
        
        return base_profile
    
    def _deduplicate_campaigns(self, campaigns: List[CampaignData]) -> List[CampaignData]:
        """Remove duplicate campaigns"""
        seen_titles = set()
        unique_campaigns = []
        
        # Sort by confidence score (highest first)
        sorted_campaigns = sorted(campaigns, key=lambda c: c.confidence_score, reverse=True)
        
        for campaign in sorted_campaigns:
            # Create a normalized title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', campaign.title.lower()).strip()
            
            if normalized_title not in seen_titles and len(normalized_title) > 5:
                seen_titles.add(normalized_title)
                unique_campaigns.append(campaign)
        
        return unique_campaigns[:20]  # Limit to top 20 campaigns
    
    async def _generate_competitive_analysis(self, organization_name: str, profile: OrganizationProfile) -> Dict[str, Any]:
        """Generate competitive analysis"""
        try:
            # Identify potential competitors based on sector and focus areas
            competitors = []
            
            # This is a simplified implementation
            # In practice, you'd use more sophisticated competitor identification
            sector_competitors = {
                'Non-profit': ['Oxfam', 'Save the Children', 'Doctors Without Borders'],
                'International': ['World Bank', 'UNDP', 'UNICEF'],
                'Environmental': ['WWF', 'Greenpeace', 'Conservation International']
            }
            
            if profile.sector in sector_competitors:
                competitors = sector_competitors[profile.sector][:3]
            
            # Focus area competitors
            focus_competitors = {
                'climate': ['Climate Action Network', 'Climate Reality Project'],
                'environment': ['Environmental Defense Fund', 'Natural Resources Defense Council'],
                'health': ['World Health Organization', 'Partners In Health'],
                'education': ['UNESCO', 'Room to Read']
            }
            
            for focus_area in profile.key_focus_areas[:3]:
                if focus_area.lower() in focus_competitors:
                    competitors.extend(focus_competitors[focus_area.lower()][:2])
            
            # Remove duplicates and the organization itself
            competitors = list(set(competitors))
            if organization_name in competitors:
                competitors.remove(organization_name)
            
            competitive_analysis = {
                'identified_competitors': competitors[:5],
                'competitive_advantages': self._identify_competitive_advantages(profile),
                'market_position': self._assess_market_position(profile),
                'differentiation_factors': self._identify_differentiation_factors(profile)
            }
            
            return competitive_analysis
            
        except Exception as e:
            logger.warning(f"Competitive analysis failed for {organization_name}: {e}")
            return {}
    
    def _identify_competitive_advantages(self, profile: OrganizationProfile) -> List[str]:
        """Identify competitive advantages"""
        advantages = []
        
        # Geographic presence
        if len(profile.geographic_presence) > 5:
            advantages.append("Strong global presence")
        
        # Partnerships
        if len(profile.partnerships) > 3:
            advantages.append("Extensive partnership network")
        
        # Awards and recognition
        if len(profile.awards_recognition) > 2:
            advantages.append("Award-winning organization")
        
        # Leadership
        if len(profile.leadership) > 5:
            advantages.append("Strong leadership team")
        
        # Focus areas
        if len(profile.key_focus_areas) > 5:
            advantages.append("Diverse expertise areas")
        
        return advantages
    
    def _assess_market_position(self, profile: OrganizationProfile) -> str:
        """Assess market position"""
        score = 0
        
        # Scoring factors
        if profile.confidence_score > 0.8:
            score += 2
        if len(profile.partnerships) > 5:
            score += 2
        if len(profile.awards_recognition) > 3:
            score += 2
        if len(profile.geographic_presence) > 10:
            score += 2
        if profile.founded_year and datetime.now().year - profile.founded_year > 20:
            score += 1
        
        if score >= 7:
            return "Market Leader"
        elif score >= 5:
            return "Strong Player"
        elif score >= 3:
            return "Established Player"
        else:
            return "Emerging Player"
    
    def _identify_differentiation_factors(self, profile: OrganizationProfile) -> List[str]:
        """Identify differentiation factors"""
        factors = []
        
        # Unique focus areas
        unique_areas = ['data visualization', 'multimedia', 'youth', 'climate']
        for area in profile.key_focus_areas:
            if area.lower() in unique_areas:
                factors.append(f"Specialized in {area}")
        
        # Geographic uniqueness
        unique_regions = ['africa', 'sub-saharan', 'middle east', 'eastern europe']
        for region in profile.geographic_presence:
            if any(unique in region.lower() for unique in unique_regions):
                factors.append(f"Strong presence in {region}")
        
        # Mission uniqueness
        if 'innovation' in profile.mission_statement.lower():
            factors.append("Innovation-focused approach")
        
        if 'community' in profile.mission_statement.lower():
            factors.append("Community-centered approach")
        
        return factors[:5]
    
    def _generate_research_summary(self, profile: OrganizationProfile, campaigns: List[CampaignData], 
                                 social_metrics: List[SocialMediaMetrics]) -> str:
        """Generate research summary"""
        summary_parts = []
        
        # Organization overview
        summary_parts.append(f"Organization: {profile.name}")
        summary_parts.append(f"Sector: {profile.sector}")
        summary_parts.append(f"Headquarters: {profile.headquarters}")
        
        if profile.founded_year:
            summary_parts.append(f"Founded: {profile.founded_year}")
        
        # Key focus areas
        if profile.key_focus_areas:
            summary_parts.append(f"Key Focus Areas: {', '.join(profile.key_focus_areas[:5])}")
        
        # Geographic presence
        if profile.geographic_presence:
            summary_parts.append(f"Geographic Presence: {', '.join(profile.geographic_presence[:5])}")
        
        # Campaign analysis
        if campaigns:
            summary_parts.append(f"\nCampaign Analysis:")
            summary_parts.append(f"- {len(campaigns)} campaigns identified")
            
            campaign_types = {}
            for campaign in campaigns:
                campaign_types[campaign.campaign_type] = campaign_types.get(campaign.campaign_type, 0) + 1
            
            if campaign_types:
                top_type = max(campaign_types, key=campaign_types.get)
                summary_parts.append(f"- Primary campaign type: {top_type}")
        
        # Social media presence
        if social_metrics:
            summary_parts.append(f"\nSocial Media Presence:")
            for metric in social_metrics:
                if metric.followers_count:
                    summary_parts.append(f"- {metric.platform}: {metric.followers_count:,} followers")
        
        # Confidence assessment
        summary_parts.append(f"\nData Confidence: {profile.confidence_score:.1%}")
        
        return "\n".join(summary_parts)
    
    def _generate_recommendations(self, profile: OrganizationProfile, campaigns: List[CampaignData], 
                                social_metrics: List[SocialMediaMetrics]) -> List[str]:
        """Generate recommendations based on research"""
        recommendations = []
        
        # Partnership recommendations
        if len(profile.partnerships) < 3:
            recommendations.append("Consider developing strategic partnerships to expand reach and capabilities")
        
        # Geographic expansion
        if len(profile.geographic_presence) < 5:
            recommendations.append("Explore opportunities for geographic expansion in underserved markets")
        
        # Digital presence
        if not social_metrics or all(not m.followers_count or m.followers_count < 10000 for m in social_metrics):
            recommendations.append("Strengthen digital and social media presence to increase visibility")
        
        # Campaign diversity
        if campaigns:
            campaign_types = set(c.campaign_type for c in campaigns)
            if len(campaign_types) < 3:
                recommendations.append("Diversify campaign types to reach broader audiences")
        
        # Focus area alignment
        rfp_friendly_areas = ['climate', 'environment', 'health', 'education', 'development']
        aligned_areas = [area for area in profile.key_focus_areas if area.lower() in rfp_friendly_areas]
        
        if len(aligned_areas) >= 2:
            recommendations.append(f"Strong alignment with RFP-friendly focus areas: {', '.join(aligned_areas)}")
        
        # Leadership visibility
        if len(profile.leadership) < 3:
            recommendations.append("Increase leadership visibility and thought leadership presence")
        
        return recommendations[:5]
    
    def get_researcher_status(self) -> Dict[str, Any]:
        """Get status of all researchers"""
        return {
            'researchers': {
                name: researcher.get_researcher_name()
                for name, researcher in self.researchers.items()
            },
            'primary_researcher': self.primary_researcher.get_researcher_name(),
            'libraries': {
                'selenium': SELENIUM_AVAILABLE,
                'twitter_api': TWITTER_API_AVAILABLE,
                'facebook_api': FACEBOOK_API_AVAILABLE
            },
            'config': {
                'max_concurrent_research': self.max_concurrent_research,
                'enable_comprehensive_research': self.enable_comprehensive_research
            }
        }
    
    async def test_researchers(self) -> Dict[str, Any]:
        """Test all researchers with sample organization"""
        test_org = "World Wildlife Fund"
        test_results = {}
        
        for name, researcher in self.researchers.items():
            try:
                start_time = asyncio.get_event_loop().time()
                
                # Test organization research
                profile = await researcher.research_organization(test_org)
                
                # Test campaign research
                campaigns = await researcher.research_campaigns(test_org)
                
                end_time = asyncio.get_event_loop().time()
                
                test_results[name] = {
                    'status': 'success',
                    'processing_time': end_time - start_time,
                    'profile_confidence': profile.confidence_score,
                    'campaigns_found': len(campaigns),
                    'focus_areas_found': len(profile.key_focus_areas),
                    'social_handles_found': len(profile.social_media_handles)
                }
                
            except Exception as e:
                test_results[name] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        return test_results

# Example usage and testing
async def main():
    """Example usage of Organization Research Module"""
    
    # Initialize module
    config = {
        'primary_researcher': 'web',
        'use_selenium': True,
        'max_concurrent_research': 2,
        'enable_comprehensive_research': True,
        'social_media_api_keys': {
            # Add your API keys here for testing
            # 'twitter': {
            #     'consumer_key': 'your_key',
            #     'consumer_secret': 'your_secret',
            #     'access_token': 'your_token',
            #     'access_token_secret': 'your_token_secret'
            # }
        }
    }
    
    research_module = OrganizationResearchModule(config)
    
    # Show researcher status
    print("Researcher Status:")
    status = research_module.get_researcher_status()
    print(f"Available researchers: {list(status['researchers'].keys())}")
    print(f"Primary researcher: {status['primary_researcher']}")
    print(f"Library availability: {status['libraries']}")
    
    # Test researchers
    print("\nTesting researchers...")
    test_results = await research_module.test_researchers()
    print(json.dumps(test_results, indent=2, default=str))
    
    # Example comprehensive research
    test_organization = "UNICEF"
    print(f"\nConducting comprehensive research on {test_organization}...")
    
    result = await research_module.research_organization_comprehensive(test_organization)
    
    if result.success:
        print(f"Research completed successfully!")
        print(f"Processing time: {result.processing_time:.2f}s")
        print(f"Organization confidence: {result.organization_profile.confidence_score:.2f}")
        print(f"Campaigns found: {len(result.campaigns)}")
        print(f"Social media platforms: {len(result.social_media_metrics)}")
        
        print(f"\nOrganization Profile:")
        print(f"- Name: {result.organization_profile.name}")
        print(f"- Sector: {result.organization_profile.sector}")
        print(f"- Headquarters: {result.organization_profile.headquarters}")
        print(f"- Website: {result.organization_profile.website}")
        print(f"- Focus Areas: {', '.join(result.organization_profile.key_focus_areas[:5])}")
        print(f"- Geographic Presence: {', '.join(result.organization_profile.geographic_presence[:5])}")
        
        if result.campaigns:
            print(f"\nTop Campaigns:")
            for campaign in result.campaigns[:3]:
                print(f"- {campaign.title} ({campaign.campaign_type})")
        
        if result.social_media_metrics:
            print(f"\nSocial Media Metrics:")
            for metric in result.social_media_metrics:
                followers = f"{metric.followers_count:,}" if metric.followers_count else "Unknown"
                print(f"- {metric.platform}: @{metric.handle} ({followers} followers)")
        
        print(f"\nRecommendations:")
        for rec in result.recommendations:
            print(f"- {rec}")
    
    else:
        print(f"Research failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
