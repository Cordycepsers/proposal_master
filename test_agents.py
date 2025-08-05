"""
Simple test to debug the agent initialization issue.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

async def test_basic_import():
    """Test basic agent imports."""
    try:
        from agents.document_parser_agent import DocumentParserAgent
        print("✅ DocumentParserAgent imported successfully")
        
        # Test initialization
        agent = DocumentParserAgent()
        print("✅ DocumentParserAgent initialized successfully")
        
        from agents.requirement_extraction_agent import RequirementExtractionAgent
        print("✅ RequirementExtractionAgent imported successfully")
        
        # Test initialization
        agent = RequirementExtractionAgent()
        print("✅ RequirementExtractionAgent initialized successfully")
        
        from agents.risk_assessment_agent import RiskAssessmentAgent
        print("✅ RiskAssessmentAgent imported successfully")
        
        # Test initialization
        agent = RiskAssessmentAgent()
        print("✅ RiskAssessmentAgent initialized successfully")
        
        print("\n🎉 All agents imported and initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic_import())
