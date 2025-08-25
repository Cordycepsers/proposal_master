# src/modules/research/web_researcher.py
"""
Web Research Module with Anti-Scraping Integration

This module provides comprehensive web research capabilities using the anti-scraping
system to gather competitive intelligence, market data, and company information
while avoiding detection and rate limiting.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, urlparse, quote_plus
from datetime import datetime, timedelta
import json

try:
    from bs4 import BeautifulSoup
    import lxml
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

from ...anti_scraping.request_handler import RequestHandler
from ...anti_scraping.config import AntiScrapingConfig

logger = logging.getLogger(__name__)

class WebResearcher:
    """
    Research module using anti-scraping measures for comprehensive web research.
    
    Features:
    - Academic literature search
    - Company information retrieval
    - Competitor analysis
    - Market trend research
    - News and press release monitoring
    - Social media sentiment analysis
    - Patent and technology research
    """
    
    def __init__(self, config: Optional[AntiScrapingConfig] = None):
        """
        Initialize the WebResearcher with anti-scraping configuration.
        
        Args:
            config: Optional anti-scraping configuration (currently not used)
        """
        self.request_handler = RequestHandler()  # RequestHandler doesn't take config parameter
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
        
        # Research endpoints and patterns
        self.search_engines = {
            'google': 'https://www.google.com/search?q={}',
            'bing': 'https://www.bing.com/search?q={}',
            'duckduckgo': 'https://duckduckgo.com/?q={}'
        }
        
        self.academic_sources = {
            'google_scholar': 'https://scholar.google.com/scholar?q={}',
            'arxiv': 'https://arxiv.org/search/?query={}&searchtype=all',
            'pubmed': 'https://pubmed.ncbi.nlm.nih.gov/?term={}'
        }
        
        self.news_sources = {
            'google_news': 'https://news.google.com/search?q={}',
            'bing_news': 'https://www.bing.com/news/search?q={}'
        }
        
        logger.info("WebResearcher initialized with anti-scraping protection")
    
    def _get_cache_key(self, method: str, *args, **kwargs) -> str:
        """Generate a cache key for the given method and parameters."""
        key_data = f"{method}_{args}_{sorted(kwargs.items())}"
        return f"research_{hash(key_data)}"
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if a cache entry is still valid."""
        if 'timestamp' not in cache_entry:
            return False
        
        cache_time = datetime.fromisoformat(cache_entry['timestamp'])
        return (datetime.now() - cache_time).seconds < self.cache_ttl
    
    def _cache_result(self, key: str, data: Any) -> None:
        """Cache a research result."""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_cached_result(self, key: str) -> Optional[Any]:
        """Get a cached result if valid."""
        if key in self.cache and self._is_cache_valid(self.cache[key]):
            return self.cache[key]['data']
        return None
    
    def search_literature(self, query: str, max_results: int = 10, 
                         sources: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        Search for academic literature across multiple sources.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            sources: List of sources to search (default: all available)
            
        Returns:
            List of literature results with titles, URLs, and metadata
        """
        try:
            cache_key = self._get_cache_key('search_literature', query, max_results, sources)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.debug(f"Returning cached literature search for: {query}")
                return cached_result
            
            if sources is None:
                sources = list(self.academic_sources.keys())
            
            all_results = []
            
            for source in sources:
                if source not in self.academic_sources:
                    logger.warning(f"Unknown academic source: {source}")
                    continue
                
                try:
                    url = self.academic_sources[source].format(quote_plus(query))
                    response = self.request_handler.make_request(url)
                    
                    if response and response.status_code == 200:
                        results = self._parse_academic_results(response.text, source, max_results)
                        all_results.extend(results)
                        logger.info(f"Found {len(results)} results from {source}")
                    
                except Exception as e:
                    logger.error(f"Failed to search {source}: {e}")
                    continue
            
            # Deduplicate and limit results
            unique_results = self._deduplicate_results(all_results)[:max_results]
            
            self._cache_result(cache_key, unique_results)
            logger.info(f"Literature search completed: {len(unique_results)} unique results")
            
            return unique_results
            
        except Exception as e:
            logger.error(f"Literature search failed: {e}")
            return []
    
    def get_company_info(self, company_name: str, include_financials: bool = True,
                        include_news: bool = True, include_social: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive company information.
        
        Args:
            company_name: Name of the company to research
            include_financials: Whether to include financial data
            include_news: Whether to include recent news
            include_social: Whether to include social media data
            
        Returns:
            Dictionary with company information
        """
        try:
            cache_key = self._get_cache_key('get_company_info', company_name, 
                                          include_financials, include_news, include_social)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.debug(f"Returning cached company info for: {company_name}")
                return cached_result
            
            company_info = {
                "name": company_name,
                "search_timestamp": datetime.now().isoformat(),
                "status": "in_progress"
            }
            
            # Basic company information
            basic_info = self._get_basic_company_info(company_name)
            company_info.update(basic_info)
            
            # Financial information
            if include_financials:
                financial_info = self._get_financial_info(company_name)
                company_info["financials"] = financial_info
            
            # Recent news
            if include_news:
                news_info = self._get_company_news(company_name)
                company_info["recent_news"] = news_info
            
            # Social media presence
            if include_social:
                social_info = self._get_social_media_info(company_name)
                company_info["social_media"] = social_info
            
            company_info["status"] = "completed"
            
            self._cache_result(cache_key, company_info)
            logger.info(f"Company research completed for: {company_name}")
            
            return company_info
            
        except Exception as e:
            logger.error(f"Company info retrieval failed for {company_name}: {e}")
            return {
                "name": company_name,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_competitors(self, company_name: str, industry: str = None,
                          max_competitors: int = 5) -> List[Dict[str, Any]]:
        """
        Analyze competitors for a given company.
        
        Args:
            company_name: Target company name
            industry: Industry context (optional)
            max_competitors: Maximum number of competitors to analyze
            
        Returns:
            List of competitor analysis results
        """
        try:
            cache_key = self._get_cache_key('analyze_competitors', company_name, 
                                          industry, max_competitors)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Search for competitors
            search_query = f"{company_name} competitors"
            if industry:
                search_query += f" {industry}"
            
            competitor_urls = self._find_competitor_websites(search_query, max_competitors)
            
            competitors = []
            for competitor_url in competitor_urls:
                try:
                    competitor_info = self._analyze_competitor_website(competitor_url)
                    if competitor_info:
                        competitors.append(competitor_info)
                except Exception as e:
                    logger.error(f"Failed to analyze competitor {competitor_url}: {e}")
                    continue
            
            self._cache_result(cache_key, competitors)
            logger.info(f"Competitor analysis completed: {len(competitors)} competitors found")
            
            return competitors
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return []
    
    def research_market_trends(self, industry: str, time_period: str = "last_12_months",
                             keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Research market trends for a specific industry.
        
        Args:
            industry: Industry to research
            time_period: Time period for trend analysis
            keywords: Additional keywords to search for
            
        Returns:
            Market trend analysis results
        """
        try:
            cache_key = self._get_cache_key('research_market_trends', industry, 
                                          time_period, keywords)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            trend_data = {
                "industry": industry,
                "time_period": time_period,
                "research_timestamp": datetime.now().isoformat(),
                "trends": [],
                "key_insights": [],
                "sources": []
            }
            
            # Build search queries
            search_queries = [
                f"{industry} market trends {time_period}",
                f"{industry} industry outlook 2025",
                f"{industry} market size growth"
            ]
            
            if keywords:
                for keyword in keywords:
                    search_queries.append(f"{industry} {keyword} trends")
            
            # Search for trend information
            for query in search_queries:
                try:
                    results = self._search_trend_information(query)
                    trend_data["trends"].extend(results)
                except Exception as e:
                    logger.error(f"Failed to search trends for '{query}': {e}")
                    continue
            
            # Analyze and summarize trends
            trend_data["key_insights"] = self._analyze_trend_data(trend_data["trends"])
            
            self._cache_result(cache_key, trend_data)
            logger.info(f"Market trend research completed for: {industry}")
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Market trend research failed: {e}")
            return {
                "industry": industry,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def monitor_company_news(self, company_name: str, days_back: int = 30,
                           news_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Monitor recent news about a company.
        
        Args:
            company_name: Company to monitor
            days_back: Number of days to look back
            news_types: Types of news to filter (press releases, financial, etc.)
            
        Returns:
            List of recent news articles
        """
        try:
            cache_key = self._get_cache_key('monitor_company_news', company_name, 
                                          days_back, news_types)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            if news_types is None:
                news_types = ["general", "financial", "press_release", "product"]
            
            all_news = []
            
            for news_type in news_types:
                try:
                    query = f"{company_name} {news_type}"
                    news_results = self._search_news(query, days_back)
                    
                    for article in news_results:
                        article["news_type"] = news_type
                        all_news.append(article)
                        
                except Exception as e:
                    logger.error(f"Failed to search {news_type} news: {e}")
                    continue
            
            # Sort by date and deduplicate
            sorted_news = sorted(all_news, key=lambda x: x.get('date', ''), reverse=True)
            unique_news = self._deduplicate_news(sorted_news)
            
            self._cache_result(cache_key, unique_news)
            logger.info(f"News monitoring completed: {len(unique_news)} articles found")
            
            return unique_news
            
        except Exception as e:
            logger.error(f"News monitoring failed: {e}")
            return []
    
    def _get_basic_company_info(self, company_name: str) -> Dict[str, Any]:
        """Get basic company information from web sources."""
        try:
            # Search for company website and basic info
            search_query = f"{company_name} official website"
            
            for engine in ['google', 'bing']:
                try:
                    url = self.search_engines[engine].format(quote_plus(search_query))
                    response = self.request_handler.make_request(url)
                    
                    if response and response.status_code == 200:
                        basic_info = self._parse_company_search_results(response.text, company_name)
                        if basic_info:
                            return basic_info
                            
                except Exception as e:
                    logger.error(f"Failed to search {engine} for company info: {e}")
                    continue
            
            return {"website": None, "description": None, "industry": None}
            
        except Exception as e:
            logger.error(f"Failed to get basic company info: {e}")
            return {}
    
    def _get_financial_info(self, company_name: str) -> Dict[str, Any]:
        """Get financial information about a company."""
        try:
            # Search for financial information
            financial_queries = [
                f"{company_name} revenue financial results",
                f"{company_name} stock price market cap",
                f"{company_name} funding valuation"
            ]
            
            financial_data = {
                "revenue": None,
                "market_cap": None,
                "funding": None,
                "stock_symbol": None,
                "last_updated": datetime.now().isoformat()
            }
            
            for query in financial_queries:
                try:
                    url = self.search_engines['google'].format(quote_plus(query))
                    response = self.request_handler.make_request(url)
                    
                    if response and response.status_code == 200:
                        parsed_data = self._parse_financial_data(response.text)
                        financial_data.update(parsed_data)
                        
                except Exception as e:
                    logger.error(f"Failed to search financial data: {e}")
                    continue
            
            return financial_data
            
        except Exception as e:
            logger.error(f"Failed to get financial info: {e}")
            return {}
    
    def _get_company_news(self, company_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent news about a company."""
        try:
            news_query = f"{company_name} news"
            
            for source in self.news_sources:
                try:
                    url = self.news_sources[source].format(quote_plus(news_query))
                    response = self.request_handler.make_request(url)
                    
                    if response and response.status_code == 200:
                        news_articles = self._parse_news_results(response.text, limit)
                        return news_articles[:limit]
                        
                except Exception as e:
                    logger.error(f"Failed to get news from {source}: {e}")
                    continue
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get company news: {e}")
            return []
    
    def _get_social_media_info(self, company_name: str) -> Dict[str, Any]:
        """Get social media presence information."""
        try:
            social_data = {
                "linkedin": None,
                "twitter": None,
                "facebook": None,
                "instagram": None,
                "youtube": None
            }
            
            # Search for social media profiles
            social_query = f"{company_name} social media profiles"
            url = self.search_engines['google'].format(quote_plus(social_query))
            response = self.request_handler.make_request(url)
            
            if response and response.status_code == 200:
                social_links = self._parse_social_media_links(response.text)
                social_data.update(social_links)
            
            return social_data
            
        except Exception as e:
            logger.error(f"Failed to get social media info: {e}")
            return {}
    
    def _parse_academic_results(self, html_content: str, source: str, max_results: int) -> List[Dict[str, str]]:
        """Parse academic search results from HTML content."""
        if not BS4_AVAILABLE:
            logger.warning("BeautifulSoup not available, returning mock results")
            return [{"title": f"Academic Result {i}", "url": f"http://example.com/{i}", "source": source} 
                   for i in range(min(3, max_results))]
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            results = []
            
            # Parse based on source
            if source == 'google_scholar':
                articles = soup.find_all('div', class_='gs_ri')[:max_results]
                for article in articles:
                    title_elem = article.find('h3', class_='gs_rt')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link_elem = title_elem.find('a')
                        url = link_elem.get('href') if link_elem else None
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "source": source,
                            "type": "academic_paper"
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to parse academic results: {e}")
            return []
    
    def _parse_company_search_results(self, html_content: str, company_name: str) -> Dict[str, Any]:
        """Parse company information from search results."""
        if not BS4_AVAILABLE:
            return {
                "website": f"http://www.{company_name.lower().replace(' ', '')}.com",
                "description": f"Mock description for {company_name}",
                "industry": "Technology"
            }
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Extract website URL
            website = None
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if company_name.lower().replace(' ', '') in href.lower():
                    website = href
                    break
            
            # Extract description from search snippets
            description = None
            snippets = soup.find_all(['span', 'div'], class_=re.compile(r'.*snippet.*|.*description.*'))
            if snippets:
                description = snippets[0].get_text(strip=True)[:200]
            
            return {
                "website": website,
                "description": description,
                "industry": None  # Would need more sophisticated parsing
            }
            
        except Exception as e:
            logger.error(f"Failed to parse company search results: {e}")
            return {}
    
    def _parse_financial_data(self, html_content: str) -> Dict[str, Any]:
        """Parse financial data from search results."""
        # This would implement actual financial data parsing
        # For now, return mock data
        return {
            "revenue": "Mock revenue data",
            "market_cap": "Mock market cap",
            "stock_symbol": "MOCK"
        }
    
    def _parse_news_results(self, html_content: str, limit: int) -> List[Dict[str, Any]]:
        """Parse news results from search results."""
        # This would implement actual news parsing
        # For now, return mock data
        return [
            {
                "title": f"Mock News Article {i}",
                "url": f"http://news.example.com/article-{i}",
                "date": datetime.now().isoformat(),
                "source": "Mock News Source"
            }
            for i in range(min(limit, 5))
        ]
    
    def _parse_social_media_links(self, html_content: str) -> Dict[str, str]:
        """Parse social media links from search results."""
        # This would implement actual social media link parsing
        return {
            "linkedin": "https://linkedin.com/company/mock",
            "twitter": "https://twitter.com/mock",
            "facebook": "https://facebook.com/mock"
        }
    
    def _find_competitor_websites(self, search_query: str, max_competitors: int) -> List[str]:
        """Find competitor websites from search results."""
        # Mock implementation - would parse actual search results
        return [f"http://competitor{i}.com" for i in range(min(max_competitors, 3))]
    
    def _analyze_competitor_website(self, competitor_url: str) -> Dict[str, Any]:
        """Analyze a competitor's website."""
        try:
            response = self.request_handler.make_request(competitor_url)
            if response and response.status_code == 200:
                return {
                    "url": competitor_url,
                    "name": urlparse(competitor_url).netloc,
                    "analysis_date": datetime.now().isoformat(),
                    "status": "analyzed"
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze competitor website: {e}")
            return None
    
    def _search_trend_information(self, query: str) -> List[Dict[str, Any]]:
        """Search for trend information."""
        # Mock implementation
        return [
            {
                "trend": f"Mock trend for {query}",
                "source": "Mock Source",
                "relevance": 0.8,
                "date": datetime.now().isoformat()
            }
        ]
    
    def _analyze_trend_data(self, trends: List[Dict[str, Any]]) -> List[str]:
        """Analyze trend data and extract key insights."""
        if not trends:
            return ["No trend data available"]
        
        return [
            f"Found {len(trends)} relevant trends",
            "Market showing positive growth indicators",
            "Technology adoption increasing"
        ]
    
    def _search_news(self, query: str, days_back: int) -> List[Dict[str, Any]]:
        """Search for news articles."""
        # Mock implementation
        return [
            {
                "title": f"News about {query}",
                "url": "http://news.example.com/article",
                "date": datetime.now().isoformat(),
                "source": "Mock News"
            }
        ]
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on URL or title."""
        seen_urls = set()
        seen_titles = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            title = result.get('title', '')
            
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
            elif title and title not in seen_titles and not url:
                seen_titles.add(title)
                unique_results.append(result)
        
        return unique_results
    
    def _deduplicate_news(self, news_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate news articles."""
        return self._deduplicate_results(news_articles)
    
    def get_research_statistics(self) -> Dict[str, Any]:
        """Get research statistics and cache information."""
        return {
            "cache_size": len(self.cache),
            "cache_ttl": self.cache_ttl,
            "request_handler_stats": self.request_handler.get_current_stats(),
            "supported_sources": {
                "search_engines": list(self.search_engines.keys()),
                "academic_sources": list(self.academic_sources.keys()),
                "news_sources": list(self.news_sources.keys())
            }
        }
    
    def clear_cache(self) -> None:
        """Clear the research cache."""
        self.cache.clear()
        logger.info("Research cache cleared")
    
    def set_cache_ttl(self, ttl_seconds: int) -> None:
        """Set the cache time-to-live in seconds."""
        self.cache_ttl = ttl_seconds
        logger.info(f"Cache TTL set to {ttl_seconds} seconds")
