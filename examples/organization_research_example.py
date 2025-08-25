"""
Example usage of the Organization Research Module

This example demonstrates how to use the organization research module
for comprehensive organization profiling and campaign analysis.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.modules.research import (
    OrganizationResearcher,
    OrganizationProfile,
    CampaignData,
    SocialMediaMetrics,
    save_research_result,
    load_research_result
)

async def main():
    """Main example function"""
    
    # Initialize the researcher
    researcher = OrganizationResearcher()
    
    # Example 1: Quick organization profile research
    print("=== Example 1: Quick Organization Profile ===")
    profile = await researcher.quick_profile_research(
        organization_name="Habitat for Humanity",
        website="https://www.habitat.org"
    )
    
    print(f"Name: {profile.name}")
    print(f"Website: {profile.website}")
    print(f"Description: {profile.description}")
    print(f"Confidence: {profile.confidence_score}")
    
    # Example 2: Comprehensive research
    print("\n=== Example 2: Comprehensive Research ===")
    result = await researcher.comprehensive_research(
        organization_name="World Wildlife Fund",
        website="https://www.worldwildlife.org",
        include_campaigns=True,
        include_social_media=True,
        campaign_keywords=["conservation", "wildlife", "climate"],
        social_platforms=["twitter", "facebook", "instagram"]
    )
    
    print(f"Organization: {result.organization_profile.name if result.organization_profile else 'None'}")
    print(f"Campaigns found: {len(result.campaigns)}")
    print(f"Social media platforms: {len(result.social_media_data)}")
    print(f"Research timestamp: {result.research_timestamp}")
    print(f"Overall confidence: {result.confidence_score:.2f}")
    
    # Example 3: Save and load research results
    print("\n=== Example 3: Save/Load Research Results ===")
    output_file = Path("research_results.json")
    
    # Save the research result
    save_research_result(result, output_file)
    print(f"Research results saved to {output_file}")
    
    # Load the research result
    loaded_result = load_research_result(output_file)
    if loaded_result:
        print(f"Successfully loaded research for: {loaded_result.organization_profile.name if loaded_result.organization_profile else 'Unknown'}")
        print(f"Loaded {len(loaded_result.campaigns)} campaigns")
        print(f"Loaded {len(loaded_result.social_media_data)} social media entries")
    
    # Example 4: Focused analyses
    print("\n=== Example 4: Focused Analyses ===")
    
    # Campaign analysis only
    campaigns = await researcher.campaign_analysis(
        organization_name="Amnesty International",
        keywords=["human rights", "advocacy", "justice"]
    )
    print(f"Found {len(campaigns)} campaigns for Amnesty International")
    
    # Social media analysis only
    social_data = await researcher.social_media_analysis(
        organization_name="Oxfam",
        platforms=["twitter", "linkedin"]
    )
    print(f"Found {len(social_data)} social media profiles for Oxfam")
    
    # Clean up
    if output_file.exists():
        output_file.unlink()
        print(f"\nCleaned up {output_file}")
    
    print("\n=== Examples completed! ===")

if __name__ == "__main__":
    asyncio.run(main())
