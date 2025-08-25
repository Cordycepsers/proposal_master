"""
Test script for Proposal Module - ContentGenerator

This script tests the ContentGenerator functionality including:
- Content generation for different proposal sections
- Content style handling
- Metrics calculation
- Recommendations generation
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append('/Users/lemaja/proposal_master')

from src.modules.proposal.content_generator import ContentGenerator


async def test_content_generator():
    """Test the ContentGenerator functionality."""
    
    print("=" * 60)
    print("TESTING PROPOSAL MODULE - CONTENT GENERATOR")
    print("=" * 60)
    
    # Initialize the content generator
    print("\n1. Initializing ContentGenerator...")
    generator = ContentGenerator()
    
    print(f"   ✓ Agent Name: {generator.name}")
    print(f"   ✓ Agent Description: {generator.description}")
    print(f"   ✓ Available Content Sections: {len(generator.content_sections)}")
    print(f"   ✓ Available Content Styles: {len(generator.content_styles)}")
    
    # Display content sections configuration
    print("\n2. Content Sections Configuration:")
    for section_name, config in list(generator.content_sections.items())[:5]:  # Show first 5
        print(f"   {section_name}:")
        print(f"     - Priority: {config['priority']}")
        print(f"     - Required: {config['required']}")
        print(f"     - Max Length: {config['max_length']} words")
        print(f"     - Description: {config['description']}")
    print(f"   ... and {len(generator.content_sections) - 5} more sections")
    
    # Display content styles
    print("\n3. Content Styles Available:")
    for style_name, style_config in generator.content_styles.items():
        print(f"   {style_name}:")
        print(f"     - Tone: {style_config['tone']}")
        print(f"     - Structure: {style_config['structure']}")
    
    # Sample input data for testing
    sample_input = {
        'requirements_analysis': {
            'summary': {
                'total_requirements': 25,
                'functional_requirements': 15,
                'technical_requirements': 8,
                'compliance_requirements': 2
            },
            'requirements': {
                'functional': [
                    'User authentication and authorization',
                    'Document management system',
                    'Reporting and analytics dashboard',
                    'Integration with existing systems'
                ],
                'technical': [
                    'Web-based application',
                    'Mobile responsive design',
                    'API integration capabilities',
                    'Database management'
                ],
                'compliance': [
                    'GDPR compliance',
                    'SOC 2 Type II certification'
                ]
            },
            'priority_requirements': [
                'Security and data protection',
                'Scalability and performance',
                'User experience optimization'
            ]
        },
        'client_profile': {
            'name': 'TechCorp Solutions',
            'industry': 'Financial Services',
            'size': 'Enterprise (500+ employees)',
            'budget_range': {'min': 100000, 'max': 250000},
            'timeline': '6 months',
            'technology_preference': 'Cloud-native solutions',
            'compliance_requirements': ['SOX', 'GDPR', 'PCI DSS']
        },
        'project_specifications': {
            'project_name': 'Digital Document Management Platform',
            'objectives': [
                'Streamline document processing workflows',
                'Improve compliance and audit capabilities',
                'Enhance user productivity and collaboration'
            ],
            'technologies': ['Python', 'React', 'PostgreSQL', 'AWS'],
            'architecture': 'Microservices',
            'deployment': 'Cloud (AWS)',
            'estimated_timeline': '6 months',
            'team_size': 8
        },
        'content_preferences': {
            'style': 'consultative',
            'sections': [
                'executive_summary',
                'project_overview', 
                'technical_approach',
                'timeline_deliverables',
                'team_qualifications',
                'budget_pricing'
            ]
        }
    }
    
    print("\n4. Testing Content Generation...")
    print("   Input Data Summary:")
    print(f"     - Client: {sample_input['client_profile']['name']}")
    print(f"     - Industry: {sample_input['client_profile']['industry']}")
    print(f"     - Project: {sample_input['project_specifications']['project_name']}")
    print(f"     - Total Requirements: {sample_input['requirements_analysis']['summary']['total_requirements']}")
    print(f"     - Content Style: {sample_input['content_preferences']['style']}")
    print(f"     - Sections Requested: {len(sample_input['content_preferences']['sections'])}")
    
    # Test the main process method
    print("\n5. Executing Content Generation Process...")
    result = await generator.process(sample_input)
    
    print(f"   Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"   ✓ Proposal ID: {result['proposal_id']}")
        
        # Display generated sections
        generated_sections = result['generated_sections']
        print(f"\n6. Generated Sections ({len(generated_sections)} total):")
        
        for section_name, section_data in generated_sections.items():
            print(f"\n   {section_name.upper().replace('_', ' ')}:")
            print(f"     - Title: {section_data['title']}")
            print(f"     - Word Count: {section_data['word_count']}")
            print(f"     - Priority: {section_data['priority']}")
            print(f"     - Required: {section_data['required']}")
            print(f"     - Generated At: {section_data['generated_at']}")
            
            # Show first 200 characters of content
            content_preview = section_data['content'][:200] + "..." if len(section_data['content']) > 200 else section_data['content']
            print(f"     - Content Preview: {content_preview}")
        
        # Display proposal structure
        proposal_structure = result['proposal_structure']
        print(f"\n7. Proposal Structure:")
        print(f"   - Total Sections: {proposal_structure['total_sections']}")
        print(f"   - Required Sections: {proposal_structure['required_sections']}")
        print(f"   - Optional Sections: {proposal_structure['optional_sections']}")
        print(f"   - Estimated Page Count: {proposal_structure['estimated_page_count']}")
        print(f"   - Section Order: {', '.join(proposal_structure['section_order'])}")
        
        # Display executive summary
        executive_summary = result['executive_summary']
        print(f"\n8. Executive Summary (first 300 chars):")
        exec_preview = executive_summary[:300] + "..." if len(executive_summary) > 300 else executive_summary
        print(f"   {exec_preview}")
        
        # Display content metrics
        content_metrics = result['content_metrics']
        print(f"\n9. Content Metrics:")
        print(f"   - Total Word Count: {content_metrics['total_word_count']}")
        print(f"   - Average Section Length: {content_metrics['average_section_length']} words")
        print(f"   - Estimated Reading Time: {content_metrics['estimated_reading_time_minutes']} minutes")
        print(f"   - Estimated Page Count: {content_metrics['estimated_page_count']} pages")
        print(f"   - Readability Score: {content_metrics['readability_score']}/10")
        
        # Display content recommendations
        content_recommendations = result['content_recommendations']
        print(f"\n10. Content Recommendations ({len(content_recommendations)} total):")
        for i, rec in enumerate(content_recommendations, 1):
            print(f"    {i}. {rec['recommendation']} (Priority: {rec['priority']})")
            print(f"       Type: {rec['type']}")
            print(f"       Rationale: {rec['rationale']}")
        
        # Display generation statistics
        generation_stats = result['generation_stats']
        print(f"\n11. Generation Statistics:")
        print(f"    - Proposals Generated: {generation_stats['proposals_generated']}")
        print(f"    - Average Word Count: {generation_stats['avg_word_count']:.0f}")
        print(f"    - Sections Created: {generation_stats['sections_created']}")
        
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test with different content style
    print("\n" + "=" * 60)
    print("TESTING WITH DIFFERENT CONTENT STYLE")
    print("=" * 60)
    
    # Test with technical style
    sample_input['content_preferences']['style'] = 'technical'
    sample_input['content_preferences']['sections'] = ['technical_approach', 'quality_assurance']
    
    print(f"\n12. Testing with '{sample_input['content_preferences']['style']}' style...")
    result2 = await generator.process(sample_input)
    
    if result2['status'] == 'success':
        print(f"    ✓ Generated {len(result2['generated_sections'])} sections")
        print(f"    ✓ Total words: {result2['content_metrics']['total_word_count']}")
        
        # Show one section content
        if 'technical_approach' in result2['generated_sections']:
            tech_section = result2['generated_sections']['technical_approach']
            print(f"\n    Technical Approach Section Preview:")
            content_preview = tech_section['content'][:400] + "..." if len(tech_section['content']) > 400 else tech_section['content']
            print(f"    {content_preview}")
    
    # Test error handling
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING")
    print("=" * 60)
    
    print("\n13. Testing with missing requirements analysis...")
    invalid_input = {'client_profile': {}, 'project_specifications': {}}
    result3 = await generator.process(invalid_input)
    
    print(f"    Status: {result3['status']}")
    if result3['status'] == 'error':
        print(f"    ✓ Error properly caught: {result3['error']}")
    
    # Get final statistics
    print("\n" + "=" * 60)
    print("FINAL STATISTICS")
    print("=" * 60)
    
    final_stats = generator.get_statistics()
    print(f"\nFinal Generation Statistics:")
    print(f"  - Total Proposals Generated: {final_stats['proposals_generated']}")
    print(f"  - Average Word Count: {final_stats['avg_word_count']:.0f}")
    print(f"  - Total Sections Created: {final_stats['sections_created']}")
    
    print("\n" + "=" * 60)
    print("PROPOSAL MODULE TESTING COMPLETE")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    asyncio.run(test_content_generator())
