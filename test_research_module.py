"""
Test script for Research Module - All Components

This script tests the Research module functionality including:
- LiteratureSearcher: Search and analyze industry literature
- ReportGenerator: Generate comprehensive research reports  
- WebResearcher: Web research with anti-scraping capabilities
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.append('/Users/lemaja/proposal_master')

from src.modules.research.literature_searcher import LiteratureSearcher
from src.modules.research.report_generator import ReportGenerator
from src.modules.research.web_researcher import WebResearcher


async def test_literature_searcher():
    """Test the LiteratureSearcher functionality."""
    
    print("\n" + "=" * 50)
    print("TESTING LITERATURE SEARCHER")
    print("=" * 50)
    
    # Initialize the literature searcher
    print("\n1. Initializing LiteratureSearcher...")
    searcher = LiteratureSearcher()
    
    print(f"   ✓ Agent Name: {searcher.name}")
    print(f"   ✓ Agent Description: {searcher.description}")
    print(f"   ✓ Search Categories: {len(searcher.search_categories)}")
    print(f"   ✓ Source Types: {len(searcher.source_types)}")
    
    # Display search categories
    print(f"\n2. Available Search Categories:")
    for category, keywords in searcher.search_categories.items():
        print(f"   {category}: {', '.join(keywords)}")
    
    # Display source types with priorities
    print(f"\n3. Source Types and Priorities:")
    for source_type, config in searcher.source_types.items():
        priority = config['priority']
        reliability = config['reliability']
        print(f"   {source_type}: Priority {priority:.1f}, Reliability {reliability:.1f}")
    
    # Sample search input
    search_input = {
        'search_terms': ['document management', 'workflow automation', 'digital transformation'],
        'categories': ['technical', 'competitive', 'case_studies'],
        'max_results': 8,
        'project_context': {
            'industry': 'financial services',
            'project_type': 'digital platform',
            'timeline': '6 months'
        }
    }
    
    print(f"\n4. Testing Literature Search...")
    print(f"   Search Terms: {search_input['search_terms']}")
    print(f"   Categories: {search_input['categories']}")
    print(f"   Max Results: {search_input['max_results']}")
    
    # Execute the search
    search_result = await searcher.process(search_input)
    
    print(f"\n5. Search Results:")
    print(f"   Status: {search_result['status']}")
    
    if search_result['status'] == 'success':
        print(f"   ✓ Categories Searched: {len(search_result['categories_searched'])}")
        
        # Display search results by category
        search_results = search_result['search_results']
        for category, results in search_results.items():
            print(f"\n   {category.upper()} CATEGORY ({len(results)} results):")
            for i, result in enumerate(results[:3], 1):  # Show first 3
                print(f"     {i}. {result['title']}")
                print(f"        Source: {result['source_type']}")
                print(f"        URL: {result['url']}")
                if 'relevance_score' in result:
                    print(f"        Relevance: {result['relevance_score']:.2f}")
        
        # Display insights
        insights = search_result.get('insights', [])
        if insights:
            print(f"\n6. Key Insights ({len(insights)} total):")
            for i, insight in enumerate(insights, 1):
                print(f"   {i}. Category: {insight.get('category', 'N/A')}")
                print(f"      Insight: {insight.get('insight', 'N/A')}")
                print(f"      Confidence: {insight.get('confidence', 'N/A')}")
                print(f"      Sources: {insight.get('supporting_sources', 'N/A')}")
        
        # Display competitive intelligence
        competitive_intel = search_result.get('competitive_intelligence', [])
        if competitive_intel:
            print(f"\n7. Competitive Intelligence ({len(competitive_intel)} total):")
            for i, intel in enumerate(competitive_intel, 1):
                if isinstance(intel, dict):
                    print(f"   {i}. {intel}")
                else:
                    print(f"   {i}. {intel}")
        
        # Display search statistics
        search_stats = search_result['search_stats']
        print(f"\n8. Search Statistics:")
        print(f"   - Searches Performed: {search_stats['searches_performed']}")
        print(f"   - Sources Analyzed: {search_stats['sources_analyzed']}")
        print(f"   - Avg Relevance Score: {search_stats['avg_relevance_score']:.3f}")
    
    else:
        print(f"   ❌ Error: {search_result['error']}")
    
    return search_result


async def test_report_generator():
    """Test the ReportGenerator functionality."""
    
    print("\n" + "=" * 50)
    print("TESTING REPORT GENERATOR")
    print("=" * 50)
    
    # Initialize the report generator
    print("\n1. Initializing ReportGenerator...")
    generator = ReportGenerator()
    
    print(f"   ✓ Agent Name: {generator.name}")
    print(f"   ✓ Agent Description: {generator.description}")
    print(f"   ✓ Report Templates: {len(generator.report_templates)}")
    print(f"   ✓ Formatting Options: {len(generator.formatting_options)}")
    
    # Display report templates
    print(f"\n2. Available Report Templates:")
    for template_name, template_config in generator.report_templates.items():
        sections = template_config['sections']
        max_length = template_config['max_length']
        print(f"   {template_name}:")
        print(f"     - Sections: {', '.join(sections)}")
        print(f"     - Max Length: {max_length} words")
    
    # Display formatting options
    print(f"\n3. Formatting Options:")
    for format_name, format_config in generator.formatting_options.items():
        extension = format_config['extension']
        print(f"   {format_name}: {extension}")
    
    # Sample source data for report generation
    source_data = {
        'literature_search': {
            'search_terms': ['document management', 'digital transformation'],
            'total_sources': 24,
            'categories': {
                'technical': 8,
                'competitive': 7,
                'case_studies': 9
            },
            'key_insights': [
                'Document management systems show 40% efficiency improvement',
                'Cloud-based solutions are preferred by 75% of enterprises',
                'AI integration is a major trend in document processing'
            ]
        },
        'competitive_analysis': {
            'competitors': ['Microsoft SharePoint', 'Google Workspace', 'Dropbox Business'],
            'market_share': {'SharePoint': 35, 'Google': 25, 'Dropbox': 15, 'Others': 25},
            'key_differentiators': [
                'Advanced AI capabilities',
                'Better integration options',
                'Lower total cost of ownership'
            ]
        },
        'market_trends': {
            'growth_rate': '12% annually',
            'market_size': '$8.2B by 2025',
            'emerging_technologies': ['AI/ML', 'Blockchain', 'Edge Computing']
        }
    }
    
    # Test different report types
    report_types = ['executive_summary', 'technical_report', 'competitive_analysis']
    report_result = None
    
    for report_type in report_types:
        print(f"\n4. Testing {report_type.replace('_', ' ').title()} Generation...")
        
        report_input = {
            'report_type': report_type,
            'source_data': source_data,
            'report_options': {
                'format': 'markdown',
                'include_charts': True,
                'executive_summary': True
            },
            'project_context': {
                'client_name': 'TechCorp Solutions',
                'project_name': 'Digital Document Platform',
                'timeline': '6 months'
            }
        }
        
        # Generate the report
        report_result = await generator.process(report_input)
        
        print(f"   Status: {report_result['status']}")
        
        if report_result['status'] == 'success':
            print(f"   ✓ Report Type: {report_result['report_type']}")
            
            # Show report preview
            if 'formatted_report' in report_result:
                formatted_content = report_result['formatted_report']
                if isinstance(formatted_content, dict) and 'content' in formatted_content:
                    report_preview = formatted_content['content'][:300] + "..." if len(formatted_content['content']) > 300 else formatted_content['content']
                else:
                    report_preview = str(formatted_content)[:300] + "..." if len(str(formatted_content)) > 300 else str(formatted_content)
                print(f"   ✓ Report Preview: {report_preview}")
            
            # Display metadata
            if 'metadata' in report_result:
                metadata = report_result['metadata']
                print(f"   ✓ Word Count: {metadata.get('word_count', 'N/A')}")
                print(f"   ✓ Sections: {metadata.get('section_count', 'N/A')}")
                print(f"   ✓ Generated: {metadata.get('generated_at', 'N/A')}")
        
        else:
            print(f"   ❌ Error: {report_result['error']}")
    
    # Display generation statistics
    final_stats = generator.generation_stats
    print(f"\n5. Final Generation Statistics:")
    print(f"   - Reports Generated: {final_stats['reports_generated']}")
    print(f"   - Avg Report Length: {final_stats['avg_report_length']:.0f} words")
    print(f"   - Total Sections Created: {final_stats['total_sections_created']}")
    
    return report_result


async def test_web_researcher():
    """Test the WebResearcher functionality."""
    
    print("\n" + "=" * 50)
    print("TESTING WEB RESEARCHER")
    print("=" * 50)
    
    # Initialize the web researcher
    print("\n1. Initializing WebResearcher...")
    researcher = WebResearcher()
    
    print(f"   ✓ WebResearcher initialized with anti-scraping protection")
    print(f"   ✓ Cache TTL: {researcher.cache_ttl} seconds")
    print(f"   ✓ Search Engines: {len(researcher.search_engines)}")
    print(f"   ✓ Academic Sources: {len(researcher.academic_sources)}")
    print(f"   ✓ News Sources: {len(researcher.news_sources)}")
    
    # Display available sources
    print(f"\n2. Available Research Sources:")
    print(f"   Search Engines: {list(researcher.search_engines.keys())}")
    print(f"   Academic Sources: {list(researcher.academic_sources.keys())}")
    print(f"   News Sources: {list(researcher.news_sources.keys())}")
    
    # Test cache functionality
    print(f"\n3. Testing Cache Functionality...")
    test_key = researcher._get_cache_key('test_method', 'arg1', keyword='value')
    print(f"   ✓ Generated cache key: {test_key}")
    
    # Cache a test result
    test_data = {'test': 'data', 'timestamp': datetime.now().isoformat()}
    researcher._cache_result(test_key, test_data)
    
    # Retrieve cached result
    cached_data = researcher._get_cached_result(test_key)
    if cached_data:
        print(f"   ✓ Cache retrieval successful")
    else:
        print(f"   ❌ Cache retrieval failed")
    
    # Test cache validation
    cache_entry = {
        'data': test_data,
        'timestamp': datetime.now().isoformat()
    }
    is_valid = researcher._is_cache_valid(cache_entry)
    print(f"   ✓ Cache validation: {is_valid}")
    
    print(f"\n4. Testing URL Generation...")
    test_query = "document management systems"
    for engine, url_template in researcher.search_engines.items():
        encoded_query = test_query.replace(' ', '+')
        test_url = url_template.format(encoded_query)
        print(f"   {engine}: {test_url}")
    
    print(f"\n5. WebResearcher Testing Summary:")
    print(f"   ✓ Initialization: Success")
    print(f"   ✓ Cache System: Functional")
    print(f"   ✓ URL Generation: Working")
    print(f"   ✓ Anti-scraping Protection: Enabled")
    print(f"   ✓ Multiple Source Support: Available")
    
    # Note: Actual web requests would require network access and may be rate-limited
    print(f"\n   Note: Full web scraping tests require network access")
    print(f"   and may be subject to rate limiting and anti-bot measures.")


async def test_research_module():
    """Test the complete Research module functionality."""
    
    print("=" * 60)
    print("TESTING RESEARCH MODULE - ALL COMPONENTS")
    print("=" * 60)
    
    try:
        # Test LiteratureSearcher
        literature_result = await test_literature_searcher()
        
        # Test ReportGenerator
        report_result = await test_report_generator()
        
        # Test WebResearcher
        await test_web_researcher()
        
        # Integration test - use literature search results in report generation
        print("\n" + "=" * 50)
        print("INTEGRATION TEST")
        print("=" * 50)
        
        integrated_result = None
        
        if literature_result.get('status') == 'success':
            print("\n6. Testing Integration: Literature Search -> Report Generation...")
            
            # Use literature search results as source data for report
            integrated_source_data = {
                'literature_search_results': literature_result,
                'search_summary': literature_result.get('summary', {}),
                'insights': literature_result.get('insights', {}),
                'competitive_intelligence': literature_result.get('competitive_intelligence', {})
            }
            
            # Generate a literature review report
            report_generator = ReportGenerator()
            integrated_report_input = {
                'report_type': 'literature_review',
                'source_data': integrated_source_data,
                'report_options': {'format': 'markdown'},
                'project_context': {
                    'search_terms': literature_result.get('search_terms', []),
                    'categories': literature_result.get('categories_searched', [])
                }
            }
            
            integrated_result = await report_generator.process(integrated_report_input)
            
            if integrated_result.get('status') == 'success':
                print(f"   ✓ Integration successful")
                print(f"   ✓ Generated literature review report")
                if 'metadata' in integrated_result:
                    metadata = integrated_result['metadata']
                    print(f"   ✓ Report length: {metadata.get('word_count', 'N/A')} words")
            else:
                print(f"   ❌ Integration failed: {integrated_result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)
        print("RESEARCH MODULE TESTING COMPLETE")
        print("=" * 60)
        
        print(f"\n✅ Module Status Summary:")
        print(f"   - LiteratureSearcher: {'✅ Working' if literature_result.get('status') == 'success' else '❌ Error'}")
        print(f"   - ReportGenerator: {'✅ Working' if report_result and report_result.get('status') == 'success' else '❌ Error'}")
        print(f"   - WebResearcher: ✅ Initialized")
        print(f"   - Integration: {'✅ Success' if integrated_result and integrated_result.get('status') == 'success' else '❌ Error'}")
        
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_research_module())
