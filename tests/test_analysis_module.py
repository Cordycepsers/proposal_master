"""
Comprehensive tests for the Analysis module components.
Tests all four main components: DocumentAnalyzer, DocumentParser, RequirementExtractor, RiskAssessor
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import json

# Import all analysis components
import sys
sys.path.append('/Users/lemaja/proposal_master/src')

from modules.analysis.document_analyzer import DocumentAnalyzer
from modules.analysis.document_parser import DocumentParser
from modules.analysis.requirement_extractor import RequirementExtractor
from modules.analysis.risk_assessor import RiskAssessor


class TestDocumentAnalyzer:
    """Test suite for DocumentAnalyzer component."""
    
    @pytest.fixture
    def analyzer(self):
        """Create DocumentAnalyzer instance for testing."""
        return DocumentAnalyzer()
    
    @pytest.fixture
    def sample_document(self):
        """Sample document content for testing."""
        return {
            'content': """
            Project Requirements Document
            
            1. Executive Summary
            The project aims to develop a web application for customer management.
            
            2. Functional Requirements
            - User authentication and authorization
            - Customer data management
            - Reporting and analytics
            - Integration with third-party services
            
            3. Technical Requirements
            - Must support 1000 concurrent users
            - 99.9% uptime requirement
            - RESTful API architecture
            - Database: PostgreSQL
            
            4. Compliance Requirements
            - GDPR compliance for EU customers
            - SOC 2 Type II certification
            - Data encryption at rest and in transit
            
            Budget: $150,000
            Timeline: 6 months
            """,
            'metadata': {
                'filename': 'project_requirements.pdf',
                'file_type': 'pdf',
                'page_count': 5
            }
        }
    
    @pytest.mark.asyncio
    async def test_analyze_document_success(self, analyzer, sample_document):
        """Test successful document analysis."""
        result = await analyzer.analyze_document(sample_document)
        
        assert result['status'] == 'success'
        assert 'document_structure' in result
        assert 'key_entities' in result
        assert 'content_themes' in result
        assert 'analysis_summary' in result
        
        # Check document structure
        structure = result['document_structure']
        assert 'sections' in structure
        assert 'word_count' in structure
        assert 'readability_score' in structure
        
        # Check key entities
        entities = result['key_entities']
        assert 'organizations' in entities
        assert 'technologies' in entities
        assert 'financial_terms' in entities
        
        # Check content themes
        themes = result['content_themes']
        assert 'primary_themes' in themes
        assert 'secondary_themes' in themes
    
    @pytest.mark.asyncio
    async def test_analyze_document_empty_content(self, analyzer):
        """Test analysis with empty content."""
        empty_doc = {'content': '', 'metadata': {}}
        result = await analyzer.analyze_document(empty_doc)
        
        assert result['status'] == 'error'
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_analyze_document_structure(self, analyzer, sample_document):
        """Test document structure analysis."""
        structure = await analyzer.analyze_document_structure(sample_document['content'])
        
        assert 'sections' in structure
        assert 'word_count' in structure
        assert 'readability_score' in structure
        assert len(structure['sections']) > 0
        
        # Check if sections are properly identified
        section_titles = [s['title'] for s in structure['sections']]
        assert any('Executive Summary' in title for title in section_titles)
        assert any('Requirements' in title for title in section_titles)
    
    @pytest.mark.asyncio
    async def test_extract_key_entities(self, analyzer, sample_document):
        """Test entity extraction."""
        entities = await analyzer.extract_key_entities(sample_document['content'])
        
        assert 'organizations' in entities
        assert 'technologies' in entities
        assert 'financial_terms' in entities
        assert 'dates' in entities
        
        # Check for expected entities
        assert len(entities['financial_terms']) > 0  # Should find $150,000
        assert len(entities['technologies']) > 0  # Should find PostgreSQL, API, etc.
    
    @pytest.mark.asyncio
    async def test_analyze_content_themes(self, analyzer, sample_document):
        """Test content theme analysis."""
        themes = await analyzer.analyze_content_themes(sample_document['content'])
        
        assert 'primary_themes' in themes
        assert 'secondary_themes' in themes
        assert 'keyword_frequency' in themes
        
        # Check theme structure
        for theme in themes['primary_themes']:
            assert 'theme' in theme
            assert 'confidence' in theme
            assert 'keywords' in theme


class TestDocumentParser:
    """Test suite for DocumentParser component."""
    
    @pytest.fixture
    def parser(self):
        """Create DocumentParser instance for testing."""
        return DocumentParser()
    
    @pytest.fixture
    def temp_files(self):
        """Create temporary test files."""
        files = {}
        
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document.\nWith multiple lines.\nAnd some content.")
            files['txt'] = f.name
        
        # Create temporary markdown file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Document\n\n## Section 1\n\nContent here.\n\n## Section 2\n\nMore content.")
            files['md'] = f.name
        
        yield files
        
        # Cleanup
        for filepath in files.values():
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    @pytest.mark.asyncio
    async def test_parse_document_txt(self, parser, temp_files):
        """Test parsing text files."""
        result = await parser.parse_document(temp_files['txt'])
        
        assert result['status'] == 'success'
        assert 'content' in result
        assert 'metadata' in result
        assert result['metadata']['file_type'] == 'txt'
        assert len(result['content']) > 0
    
    @pytest.mark.asyncio
    async def test_parse_document_md(self, parser, temp_files):
        """Test parsing markdown files."""
        result = await parser.parse_document(temp_files['md'])
        
        assert result['status'] == 'success'
        assert 'content' in result
        assert 'metadata' in result
        assert result['metadata']['file_type'] == 'md'
        assert "Test Document" in result['content']
    
    @pytest.mark.asyncio
    async def test_parse_document_nonexistent(self, parser):
        """Test parsing non-existent file."""
        result = await parser.parse_document('/nonexistent/file.txt')
        
        assert result['status'] == 'error'
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_extract_pdf_content_placeholder(self, parser):
        """Test PDF extraction placeholder functionality."""
        content = await parser._extract_pdf_content('/fake/path.pdf')
        
        # Should return placeholder content
        assert "PDF content extraction" in content
        assert "placeholder" in content.lower()
    
    @pytest.mark.asyncio
    async def test_extract_docx_content_placeholder(self, parser):
        """Test DOCX extraction placeholder functionality."""
        content = await parser._extract_docx_content('/fake/path.docx')
        
        # Should return placeholder content
        assert "DOCX content extraction" in content
        assert "placeholder" in content.lower()


class TestRequirementExtractor:
    """Test suite for RequirementExtractor component."""
    
    @pytest.fixture
    def extractor(self):
        """Create RequirementExtractor instance for testing."""
        return RequirementExtractor()
    
    @pytest.fixture
    def sample_rfp_content(self):
        """Sample RFP content for testing."""
        return """
        Request for Proposal: Customer Management System
        
        1. FUNCTIONAL REQUIREMENTS
        - The system must support user authentication and authorization
        - Users must be able to create, read, update, and delete customer records
        - The system shall generate monthly reports
        - Integration with existing CRM system is required
        - Real-time data synchronization is mandatory
        
        2. NON-FUNCTIONAL REQUIREMENTS
        - System must support 1000 concurrent users
        - Response time should be less than 2 seconds
        - 99.9% uptime requirement
        - System must be scalable to handle growth
        - Mobile responsive design is required
        
        3. COMPLIANCE REQUIREMENTS
        - Must comply with GDPR regulations
        - SOC 2 Type II certification required
        - PCI DSS compliance for payment processing
        - Data encryption at rest and in transit
        - Regular security audits must be conducted
        
        4. TECHNICAL REQUIREMENTS
        - RESTful API architecture
        - Database: PostgreSQL or MySQL
        - Cloud deployment on AWS or Azure
        - Docker containerization
        - CI/CD pipeline implementation
        
        PRIORITY: High priority for authentication features
        BUDGET: Not to exceed $200,000
        TIMELINE: Must be completed within 8 months
        """
    
    @pytest.mark.asyncio
    async def test_extract_requirements_success(self, extractor, sample_rfp_content):
        """Test successful requirement extraction."""
        result = await extractor.extract_requirements(sample_rfp_content)
        
        assert result['status'] == 'success'
        assert 'requirements' in result
        assert 'priority_analysis' in result
        assert 'summary' in result
        
        # Check requirement categories
        requirements = result['requirements']
        assert 'functional' in requirements
        assert 'non_functional' in requirements
        assert 'technical' in requirements
        assert 'compliance' in requirements
        
        # Verify requirements are not empty
        assert len(requirements['functional']) > 0
        assert len(requirements['non_functional']) > 0
        assert len(requirements['technical']) > 0
        assert len(requirements['compliance']) > 0
    
    @pytest.mark.asyncio
    async def test_extract_functional_requirements(self, extractor, sample_rfp_content):
        """Test functional requirement extraction."""
        requirements = await extractor._extract_functional_requirements(sample_rfp_content)
        
        assert len(requirements) > 0
        
        # Check requirement structure
        for req in requirements:
            assert 'id' in req
            assert 'text' in req
            assert 'priority' in req
            assert 'category' in req
        
        # Check for expected functional requirements
        req_texts = [req['text'] for req in requirements]
        assert any('authentication' in text.lower() for text in req_texts)
        assert any('customer records' in text.lower() for text in req_texts)
    
    @pytest.mark.asyncio
    async def test_extract_non_functional_requirements(self, extractor, sample_rfp_content):
        """Test non-functional requirement extraction."""
        requirements = await extractor._extract_non_functional_requirements(sample_rfp_content)
        
        assert len(requirements) > 0
        
        # Check for expected non-functional requirements
        req_texts = [req['text'] for req in requirements]
        assert any('1000 concurrent users' in text for text in req_texts)
        assert any('99.9% uptime' in text for text in req_texts)
    
    @pytest.mark.asyncio
    async def test_analyze_priority_levels(self, extractor, sample_rfp_content):
        """Test priority analysis."""
        analysis = await extractor._analyze_priority_levels(sample_rfp_content)
        
        assert 'overall_priority' in analysis
        assert 'priority_distribution' in analysis
        assert 'high_priority_items' in analysis
        
        # Check priority distribution structure
        distribution = analysis['priority_distribution']
        assert 'high' in distribution
        assert 'medium' in distribution
        assert 'low' in distribution
    
    @pytest.mark.asyncio
    async def test_extract_requirements_empty_content(self, extractor):
        """Test extraction with empty content."""
        result = await extractor.extract_requirements("")
        
        assert result['status'] == 'error'
        assert 'error' in result


class TestRiskAssessor:
    """Test suite for RiskAssessor component."""
    
    @pytest.fixture
    def assessor(self):
        """Create RiskAssessor instance for testing."""
        return RiskAssessor()
    
    @pytest.fixture
    def sample_project_data(self):
        """Sample project data for risk assessment."""
        return {
            'requirements': {
                'functional': [
                    {'id': 'FR-1', 'text': 'Complex integration with legacy systems', 'priority': 'high'},
                    {'id': 'FR-2', 'text': 'Real-time data processing', 'priority': 'medium'}
                ],
                'technical': [
                    {'id': 'TR-1', 'text': 'Microservices architecture implementation', 'priority': 'high'},
                    {'id': 'TR-2', 'text': 'Machine learning integration', 'priority': 'medium'}
                ],
                'compliance': [
                    {'id': 'CR-1', 'text': 'GDPR compliance required', 'priority': 'critical'},
                    {'id': 'CR-2', 'text': 'SOC 2 Type II certification', 'priority': 'high'}
                ]
            },
            'project_details': {
                'budget': 'Limited budget of $100,000',
                'deadline': 'Urgent delivery required in 3 months',
                'team_size': 5,
                'complexity': 'high'
            },
            'content': """
            This project involves complex system integration with legacy systems.
            Multiple third-party integrations are required.
            Tight deadline and limited resources.
            Regulatory compliance is critical.
            High availability and performance requirements.
            """
        }
    
    @pytest.mark.asyncio
    async def test_assess_project_risk_success(self, assessor, sample_project_data):
        """Test successful project risk assessment."""
        result = await assessor.assess_project_risk(
            requirements=sample_project_data['requirements'],
            project_details=sample_project_data['project_details'],
            content=sample_project_data['content']
        )
        
        assert result['status'] == 'success'
        assert 'risk_assessment' in result
        assert 'overall_risk' in result
        assert 'mitigation_strategies' in result
        assert 'risk_timeline' in result
        assert 'recommendations' in result
        
        # Check overall risk structure
        overall_risk = result['overall_risk']
        assert 'score' in overall_risk
        assert 'level' in overall_risk
        assert 'percentage' in overall_risk
        assert overall_risk['level'] in ['low', 'medium', 'high', 'critical']
    
    @pytest.mark.asyncio
    async def test_assess_risk_categories(self, assessor, sample_project_data):
        """Test risk category assessment."""
        risk_assessment = await assessor._assess_risk_categories(
            requirements=sample_project_data['requirements'],
            project_details=sample_project_data['project_details'],
            content=sample_project_data['content']
        )
        
        # Check all risk categories are assessed
        expected_categories = ['technical', 'timeline', 'budget', 'operational', 'compliance']
        for category in expected_categories:
            assert category in risk_assessment
            
            risk_data = risk_assessment[category]
            assert 'score' in risk_data
            assert 'severity' in risk_data
            assert 'indicators_found' in risk_data
            assert 'weight' in risk_data
            assert 'weighted_score' in risk_data
    
    @pytest.mark.asyncio
    async def test_generate_mitigation_strategies(self, assessor):
        """Test mitigation strategy generation."""
        # Sample risk assessment data
        risk_assessment = {
            'technical': {'score': 3.0, 'severity': 'high'},
            'timeline': {'score': 2.5, 'severity': 'high'},
            'budget': {'score': 1.5, 'severity': 'medium'},
            'operational': {'score': 0.8, 'severity': 'low'},
            'compliance': {'score': 3.2, 'severity': 'critical'}
        }
        
        strategies = await assessor._generate_mitigation_strategies(risk_assessment)
        
        # Check strategies are generated for all categories
        for category in risk_assessment.keys():
            assert category in strategies
            assert len(strategies[category]) > 0
            
            # Check strategy structure
            for strategy in strategies[category]:
                assert 'strategy' in strategy
                assert 'priority' in strategy
                assert 'timeline' in strategy
                assert 'resource_requirement' in strategy
    
    @pytest.mark.asyncio
    async def test_create_risk_timeline(self, assessor):
        """Test risk timeline creation."""
        risk_assessment = {
            'technical': {'severity': 'high'},
            'timeline': {'severity': 'critical'},
            'budget': {'severity': 'medium'}
        }
        project_details = {'deadline': '2024-06-01'}
        
        timeline = await assessor._create_risk_timeline(risk_assessment, project_details)
        
        assert len(timeline) > 0
        
        # Check timeline structure
        for event in timeline:
            assert 'date' in event
            assert 'event' in event
            assert 'type' in event
            assert 'description' in event
            assert event['type'] in ['milestone', 'action', 'review']
    
    @pytest.mark.asyncio
    async def test_calculate_overall_risk(self, assessor):
        """Test overall risk calculation."""
        risk_assessment = {
            'technical': {'weighted_score': 1.5},
            'timeline': {'weighted_score': 0.8},
            'budget': {'weighted_score': 0.3}
        }
        
        overall_risk = await assessor._calculate_overall_risk(risk_assessment)
        
        assert 'score' in overall_risk
        assert 'level' in overall_risk
        assert 'percentage' in overall_risk
        assert overall_risk['level'] in ['low', 'medium', 'high', 'critical']
        assert 0 <= overall_risk['percentage'] <= 100
    
    def test_get_severity_level(self, assessor):
        """Test severity level determination."""
        assert assessor._get_severity_level(0.5) == 'low'
        assert assessor._get_severity_level(1.5) == 'medium'
        assert assessor._get_severity_level(2.5) == 'high'
        assert assessor._get_severity_level(3.5) == 'critical'
    
    def test_get_statistics(self, assessor):
        """Test statistics retrieval."""
        stats = assessor.get_statistics()
        
        assert 'assessments_completed' in stats
        assert 'avg_risk_score' in stats
        assert 'high_risk_projects' in stats
        assert 'total_risks_identified' in stats


class TestAnalysisModuleIntegration:
    """Integration tests for the complete analysis module."""
    
    @pytest.fixture
    def analysis_components(self):
        """Create all analysis components."""
        return {
            'analyzer': DocumentAnalyzer(),
            'parser': DocumentParser(),
            'extractor': RequirementExtractor(),
            'assessor': RiskAssessor()
        }
    
    @pytest.fixture
    def complete_document(self):
        """Complete document for end-to-end testing."""
        return """
        PROJECT SPECIFICATION: Customer Portal Development
        
        1. EXECUTIVE SUMMARY
        We require a comprehensive customer portal that integrates with our existing CRM system.
        The portal must provide real-time access to customer data and support mobile devices.
        
        2. FUNCTIONAL REQUIREMENTS
        - User authentication and role-based access control
        - Customer profile management with CRUD operations
        - Real-time dashboard with analytics
        - Document management and file upload capabilities
        - Integration with Salesforce CRM
        - Email notification system
        - Search functionality across customer data
        
        3. NON-FUNCTIONAL REQUIREMENTS
        - Support for 2000 concurrent users
        - Page load time under 3 seconds
        - 99.95% uptime requirement
        - Mobile responsive design
        - Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
        - Accessibility compliance (WCAG 2.1 AA)
        
        4. TECHNICAL REQUIREMENTS
        - React.js frontend framework
        - Node.js backend with Express
        - PostgreSQL database
        - Redis for caching
        - AWS deployment with auto-scaling
        - Docker containerization
        - CI/CD pipeline with Jenkins
        - API-first architecture with OpenAPI documentation
        
        5. COMPLIANCE REQUIREMENTS
        - GDPR compliance for European customers
        - CCPA compliance for California residents
        - SOC 2 Type II audit requirements
        - PCI DSS Level 1 for payment processing
        - Regular penetration testing
        
        6. PROJECT CONSTRAINTS
        Budget: $300,000 maximum
        Timeline: 12 months from project start
        Team: 8 developers, 2 designers, 1 project manager
        Go-live date: December 2024 (non-negotiable)
        
        7. RISK FACTORS
        - Complex integration with legacy CRM system
        - Tight timeline due to business requirements
        - Multiple compliance requirements
        - High availability requirements
        - Third-party API dependencies
        """
    
    @pytest.mark.asyncio
    async def test_end_to_end_analysis_workflow(self, analysis_components, complete_document):
        """Test complete analysis workflow from document to risk assessment."""
        analyzer = analysis_components['analyzer']
        extractor = analysis_components['extractor']
        assessor = analysis_components['assessor']
        
        # Step 1: Analyze document structure and content
        document_data = {
            'content': complete_document,
            'metadata': {'filename': 'project_spec.txt', 'file_type': 'txt'}
        }
        
        analysis_result = await analyzer.analyze_document(document_data)
        assert analysis_result['status'] == 'success'
        
        # Step 2: Extract requirements
        requirements_result = await extractor.extract_requirements(complete_document)
        assert requirements_result['status'] == 'success'
        
        # Step 3: Assess project risks
        project_details = {
            'budget': '$300,000 maximum',
            'deadline': 'December 2024 (non-negotiable)',
            'team_size': 11,
            'complexity': 'high'
        }
        
        risk_result = await assessor.assess_project_risk(
            requirements=requirements_result['requirements'],
            project_details=project_details,
            content=complete_document
        )
        assert risk_result['status'] == 'success'
        
        # Verify end-to-end results
        assert len(requirements_result['requirements']['functional']) >= 5
        assert len(requirements_result['requirements']['technical']) >= 5
        assert len(requirements_result['requirements']['compliance']) >= 3
        
        # Risk assessment should identify high risks due to complexity
        assert risk_result['overall_risk']['level'] in ['medium', 'high', 'critical']
        assert len(risk_result['mitigation_strategies']) > 0
        assert len(risk_result['risk_timeline']) > 0


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
