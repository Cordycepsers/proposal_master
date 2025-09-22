#!/usr/bin/env python3
"""
Simple functional test for Analysis Module components
Tests basic functionality without complex dependencies
"""

import sys
import os
import asyncio
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.modules.analysis.document_analyzer import DocumentAnalyzer
from src.modules.analysis.document_parser import DocumentParser
from src.modules.analysis.requirement_extractor import RequirementExtractor
from src.modules.analysis.risk_assessor import RiskAssessor

async def test_document_analyzer():
    """Test DocumentAnalyzer basic functionality."""
    print("🔍 Testing DocumentAnalyzer...")
    
    analyzer = DocumentAnalyzer()
    
    # Test with sample document
    sample_doc = {
        'content': """
        Project Requirements Document
        
        1. FUNCTIONAL REQUIREMENTS
        - User authentication system
        - Dashboard with analytics
        - Customer management features
        
        2. TECHNICAL REQUIREMENTS  
        - React frontend
        - Node.js backend
        - PostgreSQL database
        
        Budget: $100,000
        Timeline: 6 months
        """,
        'metadata': {'filename': 'test.txt', 'file_type': 'txt'}
    }
    
    result = await analyzer.analyze_document(sample_doc)
    assert result['status'] == 'success'
    assert 'document_structure' in result
    assert 'key_entities' in result
    assert 'content_themes' in result
    
    print("✅ DocumentAnalyzer test passed")
    return result

async def test_document_parser():
    """Test DocumentParser basic functionality."""
    print("🔍 Testing DocumentParser...")
    
    parser = DocumentParser()
    
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document.\nWith multiple lines.\nAnd some content.")
        temp_file = f.name
    
    try:
        result = await parser.parse_document(temp_file)
        assert result['status'] == 'success'
        assert 'content' in result
        assert 'metadata' in result
        assert len(result['content']) > 0
        
        print("✅ DocumentParser test passed")
        return result
    finally:
        os.unlink(temp_file)

async def test_requirement_extractor():
    """Test RequirementExtractor basic functionality."""
    print("🔍 Testing RequirementExtractor...")
    
    extractor = RequirementExtractor()
    
    sample_rfp = """
    REQUEST FOR PROPOSAL: Customer Management System
    
    FUNCTIONAL REQUIREMENTS:
    - The system must support user authentication
    - Users shall be able to create customer records
    - The system must generate reports
    - Integration with CRM is required
    
    NON-FUNCTIONAL REQUIREMENTS:
    - System must support 1000 concurrent users
    - Response time should be under 2 seconds
    - 99.9% uptime requirement
    
    TECHNICAL REQUIREMENTS:
    - RESTful API architecture
    - PostgreSQL database
    - Cloud deployment
    
    COMPLIANCE REQUIREMENTS:
    - GDPR compliance required
    - SOC 2 certification needed
    """
    
    result = await extractor.extract_requirements(sample_rfp)
    assert result['status'] == 'success'
    assert 'requirements' in result
    assert 'functional' in result['requirements']
    assert 'non_functional' in result['requirements']
    assert 'technical' in result['requirements']
    assert 'compliance' in result['requirements']
    
    print("✅ RequirementExtractor test passed")
    return result

async def test_risk_assessor():
    """Test RiskAssessor basic functionality."""
    print("🔍 Testing RiskAssessor...")
    
    assessor = RiskAssessor()
    
    # Sample project data
    requirements = {
        'functional': [
            {'id': 'FR-1', 'text': 'Complex integration with legacy systems', 'priority': 'high'}
        ],
        'technical': [
            {'id': 'TR-1', 'text': 'Microservices architecture', 'priority': 'high'}
        ],
        'compliance': [
            {'id': 'CR-1', 'text': 'GDPR compliance required', 'priority': 'critical'}
        ]
    }
    
    project_details = {
        'budget': 'Limited budget',
        'deadline': 'Tight deadline',
        'team_size': 5
    }
    
    content = """
    Complex project with tight deadlines and limited resources.
    Multiple integrations required with legacy systems.
    Regulatory compliance is critical.
    """
    
    result = await assessor.assess_project_risk(
        requirements=requirements,
        project_details=project_details,
        content=content
    )
    
    assert result['status'] == 'success'
    assert 'risk_assessment' in result
    assert 'overall_risk' in result
    assert 'mitigation_strategies' in result
    
    print("✅ RiskAssessor test passed")
    return result

async def main():
    """Run all tests."""
    print("🚀 Starting Analysis Module Functional Tests\n")
    
    try:
        # Run all tests
        analyzer_result = await test_document_analyzer()
        parser_result = await test_document_parser()
        extractor_result = await test_requirement_extractor()
        assessor_result = await test_risk_assessor()
        
        print("\n🎉 All tests passed successfully!")
        print("\n📊 Test Results Summary:")
        print(f"   - Document Analysis: {len(analyzer_result['key_entities'])} entity categories")
        print(f"   - Document Parser: {len(parser_result['content'])} characters parsed")
        print(f"   - Requirement Extraction: {sum(len(reqs) for reqs in extractor_result['requirements'].values())} requirements found")
        print(f"   - Risk Assessment: {assessor_result['overall_risk']['level']} risk level detected")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
