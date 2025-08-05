# src/modules/research/__init__.py
"""
Research Module

This module contains specialized sub-agents for research and competitive intelligence:
- Literature Searcher: Searches and analyzes relevant industry literature and documentation  
- Report Generator: Creates comprehensive research reports and summaries
"""

from .literature_searcher import LiteratureSearcher
from .report_generator import ReportGenerator

__all__ = [
    'LiteratureSearcher',
    'ReportGenerator'
]

from .web_researcher import WebResearcher

__all__ = ['WebResearcher']

# Version information
__version__ = '1.0.0'
__author__ = 'Task Master Development Team'

# Module-level configuration
DEFAULT_CACHE_TTL = 3600  # 1 hour
DEFAULT_MAX_RESULTS = 10
DEFAULT_REQUEST_TIMEOUT = 30

# Supported research types
RESEARCH_TYPES = [
    'academic_literature',
    'company_information',
    'competitor_analysis',
    'market_trends',
    'news_monitoring',
    'social_media',
    'financial_data',
    'regulatory_information'
]

# Supported data sources
DATA_SOURCES = {
    'search_engines': ['google', 'bing', 'duckduckgo'],
    'academic': ['google_scholar', 'arxiv', 'pubmed'],
    'news': ['google_news', 'bing_news'],
    'financial': ['yahoo_finance', 'bloomberg', 'sec_filings'],
    'social': ['linkedin', 'twitter', 'facebook', 'instagram']
}
