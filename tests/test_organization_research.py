#!/usr/bin/env python3
"""
Test script for organization research module
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.modules.research.organization_research import OrganizationResearcher, OrganizationProfile

async def test_organization_research():
    """Test basic organization research functionality"""
    researcher = OrganizationResearcher()
    
    # Test quick profile research
    print("Testing organization profile research...")
    profile = await researcher.quick_profile_research("American Red Cross")
    
    print(f"Organization: {profile.name}")
    print(f"Website: {profile.website}")
    print(f"Description: {profile.description}")
    print(f"Confidence Score: {profile.confidence_score}")
    
    # Test comprehensive research
    print("\nTesting comprehensive research...")
    result = await researcher.comprehensive_research(
        "Doctors Without Borders",
        include_campaigns=True,
        include_social_media=True
    )
    
    print(f"Organization Profile: {result.organization_profile.name if result.organization_profile else 'None'}")
    print(f"Campaigns Found: {len(result.campaigns)}")
    print(f"Social Media Data: {len(result.social_media_data)}")
    print(f"Overall Confidence: {result.confidence_score}")
    print(f"Data Sources: {result.data_sources}")
    
    print("\nOrganization research module test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_organization_research())
