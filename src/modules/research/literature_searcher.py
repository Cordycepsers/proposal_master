"""
Literature Searcher Sub-Agent

Specialized sub-agent for searching and analyzing relevant industry literature,
research papers, documentation, and competitive intelligence from various sources.
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio
import re
from datetime import datetime

from ...agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class LiteratureSearcher(BaseAgent):
    """Sub-agent for literature search and competitive intelligence gathering."""
    
    def __init__(self):
        super().__init__(
            name="Literature Searcher",
            description="Searches and analyzes relevant industry literature and documentation"
        )
        
        # Search categories
        self.search_categories = {
            'technical': ['technical specifications', 'implementation guides', 'best practices'],
            'competitive': ['competitor analysis', 'market research', 'industry reports'],
            'regulatory': ['compliance requirements', 'industry standards', 'regulations'],
            'case_studies': ['success stories', 'project examples', 'use cases'],
            'trends': ['industry trends', 'emerging technologies', 'market forecasts']
        }
        
        # Source types and priorities
        self.source_types = {
            'academic': {'priority': 0.9, 'reliability': 0.95},
            'industry_report': {'priority': 0.8, 'reliability': 0.85},
            'case_study': {'priority': 0.7, 'reliability': 0.75},
            'blog_post': {'priority': 0.5, 'reliability': 0.6},
            'forum': {'priority': 0.3, 'reliability': 0.4}
        }
        
        self.search_stats = {
            'searches_performed': 0,
            'sources_analyzed': 0,
            'avg_relevance_score': 0.0
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform literature search based on project requirements.
        
        Args:
            input_data: Dictionary containing:
                - search_terms: List of search terms or keywords
                - categories: Search categories to focus on
                - max_results: Maximum number of results per category
                - project_context: Project context for relevance scoring
                
        Returns:
            Dictionary containing search results and analysis
        """
        try:
            self.log_operation("Starting literature search", input_data)
            
            search_terms = input_data.get('search_terms', [])
            categories = input_data.get('categories', list(self.search_categories.keys()))
            max_results = input_data.get('max_results', 10)
            project_context = input_data.get('project_context', {})
            
            if not search_terms:
                raise ValueError("Search terms are required")
            
            # Perform searches by category
            search_results = await self._perform_searches(search_terms, categories, max_results)
            
            # Analyze and rank results
            analyzed_results = await self._analyze_results(search_results, project_context)
            
            # Extract key insights
            insights = await self._extract_insights(analyzed_results)
            
            # Generate competitive intelligence
            competitive_intel = await self._generate_competitive_intelligence(analyzed_results)
            
            # Create search summary
            summary = await self._create_search_summary(analyzed_results, insights)
            
            # Update statistics
            total_sources = sum(len(results) for results in search_results.values())
            self.search_stats['searches_performed'] += 1
            self.search_stats['sources_analyzed'] += total_sources
            
            if analyzed_results:
                avg_relevance = sum(result['relevance_score'] for category_results in analyzed_results.values() 
                                 for result in category_results) / total_sources
                self.search_stats['avg_relevance_score'] = (
                    (self.search_stats['avg_relevance_score'] * (self.search_stats['searches_performed'] - 1) + 
                     avg_relevance) / self.search_stats['searches_performed']
                )
            
            result = {
                'status': 'success',
                'search_terms': search_terms,
                'categories_searched': categories,
                'search_results': analyzed_results,
                'insights': insights,
                'competitive_intelligence': competitive_intel,
                'summary': summary,
                'search_stats': self.search_stats.copy()
            }
            
            self.log_operation("Literature search completed", {
                'categories': len(categories),
                'total_sources': total_sources
            })
            return result
            
        except Exception as e:
            error_msg = f"Literature search failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'search_terms': input_data.get('search_terms', [])
            }
    
    async def _perform_searches(self, search_terms: List[str], categories: List[str], 
                              max_results: int) -> Dict[str, List[Dict[str, Any]]]:
        """Perform searches across different categories."""
        try:
            search_results = {}
            
            for category in categories:
                if category not in self.search_categories:
                    continue
                
                category_keywords = self.search_categories[category]
                category_results = []
                
                # Simulate search for each term + category keywords
                for search_term in search_terms:
                    for keyword in category_keywords:
                        # Simulate search results
                        results = await self._simulate_search(search_term, keyword, category, max_results // len(category_keywords))
                        category_results.extend(results)
                
                # Remove duplicates and limit results
                unique_results = self._remove_duplicates(category_results)
                search_results[category] = unique_results[:max_results]
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Search execution failed: {e}")
            return {}
    
    async def _simulate_search(self, search_term: str, keyword: str, category: str, 
                             max_results: int) -> List[Dict[str, Any]]:
        """Simulate search results (would integrate with real search APIs in production)."""
        try:
            # Simulate search delay
            await asyncio.sleep(0.1)
            
            # Generate simulated results
            results = []
            for i in range(min(max_results, 5)):  # Limit to 5 results per search
                result = {
                    'title': f"{keyword.title()} for {search_term} - Result {i+1}",
                    'url': f"https://example.com/search/{category}/{search_term.replace(' ', '-')}-{i+1}",
                    'source_type': self._determine_source_type(i),
                    'published_date': self._generate_date(),
                    'abstract': f"This {category} resource discusses {keyword} in the context of {search_term}. "
                              f"It provides comprehensive insights and practical applications.",
                    'relevance_score': 0.0,  # Will be calculated later
                    'category': category,
                    'search_term': search_term,
                    'keyword': keyword
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search simulation failed: {e}")
            return []
    
    async def _analyze_results(self, search_results: Dict[str, List[Dict[str, Any]]], 
                             project_context: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze search results and calculate relevance scores."""
        try:
            analyzed_results = {}
            
            for category, results in search_results.items():
                analyzed_category = []
                
                for result in results:
                    # Calculate relevance score
                    relevance_score = await self._calculate_relevance_score(result, project_context)
                    result['relevance_score'] = relevance_score
                    
                    # Add source reliability score
                    source_type = result.get('source_type', 'blog_post')
                    result['reliability_score'] = self.source_types.get(source_type, {}).get('reliability', 0.5)
                    
                    # Calculate overall quality score
                    result['quality_score'] = (relevance_score * 0.7 + result['reliability_score'] * 0.3)
                    
                    analyzed_category.append(result)
                
                # Sort by quality score
                analyzed_category.sort(key=lambda x: x['quality_score'], reverse=True)
                analyzed_results[category] = analyzed_category
            
            return analyzed_results
            
        except Exception as e:
            self.logger.error(f"Result analysis failed: {e}")
            return search_results
    
    async def _calculate_relevance_score(self, result: Dict[str, Any], 
                                       project_context: Dict[str, Any]) -> float:
        """Calculate relevance score based on content and project context."""
        try:
            score = 0.5  # Base score
            
            # Check title and abstract for project-relevant terms
            text_content = (result.get('title', '') + ' ' + result.get('abstract', '')).lower()
            
            # Project context matching
            project_domain = project_context.get('domain', '').lower()
            if project_domain and project_domain in text_content:
                score += 0.2
            
            project_technologies = project_context.get('technologies', [])
            for tech in project_technologies:
                if tech.lower() in text_content:
                    score += 0.1
            
            # Recency bonus
            pub_date = result.get('published_date', '')
            if '2024' in pub_date or '2023' in pub_date:
                score += 0.1
            
            # Source type priority
            source_type = result.get('source_type', 'blog_post')
            priority = self.source_types.get(source_type, {}).get('priority', 0.5)
            score = score * priority
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            self.logger.error(f"Relevance calculation failed: {e}")
            return 0.5
    
    async def _extract_insights(self, analyzed_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, str]]:
        """Extract key insights from search results."""
        try:
            insights = []
            
            # Analyze top results across categories
            for category, results in analyzed_results.items():
                top_results = results[:3]  # Top 3 results per category
                
                if not top_results:
                    continue
                
                # Extract common themes
                common_terms = self._extract_common_terms([r['abstract'] for r in top_results])
                
                insight = {
                    'category': category,
                    'insight': f"Key themes in {category} research include: {', '.join(common_terms[:5])}",
                    'confidence': 'high' if len(top_results) >= 3 else 'medium',
                    'supporting_sources': len(top_results)
                }
                insights.append(insight)
            
            # Cross-category insights
            all_abstracts = []
            for results in analyzed_results.values():
                all_abstracts.extend([r['abstract'] for r in results[:2]])
            
            if all_abstracts:
                universal_themes = self._extract_common_terms(all_abstracts)
                insights.append({
                    'category': 'cross_category',
                    'insight': f"Universal themes across all research: {', '.join(universal_themes[:3])}",
                    'confidence': 'medium',
                    'supporting_sources': len(all_abstracts)
                })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Insight extraction failed: {e}")
            return []
    
    async def _generate_competitive_intelligence(self, analyzed_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate competitive intelligence from search results."""
        try:
            competitive_intel = {
                'market_leaders': [],
                'emerging_technologies': [],
                'industry_trends': [],
                'competitive_advantages': []
            }
            
            # Analyze competitive category results
            competitive_results = analyzed_results.get('competitive', [])
            
            for result in competitive_results[:5]:  # Top 5 competitive results
                abstract = result.get('abstract', '').lower()
                
                # Extract potential market leaders (companies mentioned)
                companies = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', result.get('abstract', ''))
                competitive_intel['market_leaders'].extend(companies[:2])  # Limit to 2 per result
                
                # Extract technology mentions
                tech_terms = ['cloud', 'ai', 'machine learning', 'blockchain', 'iot', 'automation']
                found_tech = [term for term in tech_terms if term in abstract]
                competitive_intel['emerging_technologies'].extend(found_tech)
            
            # Analyze trends category
            trends_results = analyzed_results.get('trends', [])
            for result in trends_results[:3]:
                abstract = result.get('abstract', '').lower()
                
                # Extract trend indicators
                trend_indicators = ['growing', 'increasing', 'emerging', 'adoption', 'market']
                found_trends = [indicator for indicator in trend_indicators if indicator in abstract]
                competitive_intel['industry_trends'].extend(found_trends)
            
            # Remove duplicates and limit results
            for key in competitive_intel:
                competitive_intel[key] = list(set(competitive_intel[key]))[:5]
            
            return competitive_intel
            
        except Exception as e:
            self.logger.error(f"Competitive intelligence generation failed: {e}")
            return {}
    
    async def _create_search_summary(self, analyzed_results: Dict[str, List[Dict[str, Any]]], 
                                   insights: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create a summary of the search results."""
        try:
            total_sources = sum(len(results) for results in analyzed_results.values())
            high_quality_sources = sum(
                len([r for r in results if r.get('quality_score', 0) > 0.7]) 
                for results in analyzed_results.values()
            )
            
            categories_covered = len(analyzed_results)
            avg_relevance = 0.0
            
            if total_sources > 0:
                all_scores = [r['relevance_score'] for results in analyzed_results.values() for r in results]
                avg_relevance = sum(all_scores) / len(all_scores)
            
            return {
                'total_sources_found': total_sources,
                'high_quality_sources': high_quality_sources,
                'categories_covered': categories_covered,
                'average_relevance_score': round(avg_relevance, 2),
                'key_insights_generated': len(insights),
                'search_quality': 'high' if avg_relevance > 0.7 else 'medium' if avg_relevance > 0.5 else 'low'
            }
            
        except Exception as e:
            self.logger.error(f"Summary creation failed: {e}")
            return {}
    
    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on URL."""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    def _determine_source_type(self, index: int) -> str:
        """Determine source type based on index (simulation)."""
        types = ['academic', 'industry_report', 'case_study', 'blog_post', 'forum']
        return types[index % len(types)]
    
    def _generate_date(self) -> str:
        """Generate a recent publication date."""
        import random
        year = random.choice([2023, 2024])
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year}-{month:02d}-{day:02d}"
    
    def _extract_common_terms(self, texts: List[str]) -> List[str]:
        """Extract common terms from a list of texts."""
        try:
            # Simple term extraction (would use NLP in production)
            all_words = []
            for text in texts:
                words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
                all_words.extend(words)
            
            # Count word frequency
            word_count = {}
            for word in all_words:
                word_count[word] = word_count.get(word, 0) + 1
            
            # Return most common words
            common_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
            return [word for word, count in common_words[:10] if count > 1]
            
        except Exception as e:
            self.logger.error(f"Term extraction failed: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get search statistics."""
        return self.search_stats.copy()
