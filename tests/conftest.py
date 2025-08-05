# tests/conftest.py
"""
Pytest configuration and shared fixtures for Proposal Master tests.

This file contains shared test fixtures, configuration, and setup
that can be used across all test modules.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch
from typing import Dict, Any, List

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Test configuration
pytest_plugins = []

@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration settings"""
    return {
        "test_data_dir": os.path.join(PROJECT_ROOT, "tests", "test_data"),
        "temp_dir": os.path.join(PROJECT_ROOT, "tests", "temp"),
        "mock_responses": True,
        "verbose_logging": True
    }

@pytest.fixture
def sample_document():
    """Provide sample document for testing"""
    return {
        "title": "Test Project Requirements",
        "content": """
        We need a web application with the following features:
        - User authentication and authorization
        - Database integration with PostgreSQL
        - RESTful API endpoints
        - Mobile-responsive frontend
        - Payment processing integration
        - Real-time notifications
        
        Budget: $75,000
        Timeline: 4 months
        Industry: E-commerce
        """,
        "metadata": {
            "created_date": "2024-01-15",
            "file_type": "txt",
            "file_size": 1024,
            "client_id": "client_123"
        }
    }

@pytest.fixture
def sample_client_profile():
    """Provide sample client profile for testing"""
    return {
        "name": "TechCorp Solutions",
        "industry": "Technology",
        "size": "Medium",
        "location": "San Francisco, CA",
        "budget_range": "$50,000 - $100,000",
        "project_history": [
            {
                "project": "E-commerce Platform",
                "completed": True,
                "satisfaction": 4.5
            }
        ],
        "preferences": {
            "communication_style": "Professional",
            "reporting_frequency": "Weekly",
            "technologies": ["React", "Node.js", "PostgreSQL"]
        }
    }

@pytest.fixture
def sample_proposal_data():
    """Provide sample proposal data for testing"""
    return {
        "document_id": "prop_123",
        "client_id": "client_123",
        "title": "Web Application Development Proposal",
        "sections": {
            "executive_summary": "Executive summary content...",
            "problem_statement": "Problem statement content...",
            "solution_approach": "Solution approach content...",
            "timeline": "Timeline content...",
            "budget": "Budget breakdown content...",
            "team": "Team information content..."
        },
        "metadata": {
            "created_date": "2024-01-15",
            "version": "1.0",
            "status": "draft",
            "word_count": 2500
        }
    }

@pytest.fixture
def mock_anti_scraping_response():
    """Provide mock response for anti-scraping tests"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <head><title>Market Research Data</title></head>
        <body>
            <div class="competitor">
                <h3>Competitor A</h3>
                <p>Price: $60,000</p>
                <p>Rating: 4.2/5</p>
            </div>
            <div class="competitor">
                <h3>Competitor B</h3>
                <p>Price: $55,000</p>
                <p>Rating: 4.0/5</p>
            </div>
            <div class="trend">
                <p>AI integration trending upward</p>
            </div>
        </body>
    </html>
    """
    mock_response.headers = {
        'Content-Type': 'text/html',
        'Server': 'nginx/1.18.0'
    }
    return mock_response

@pytest.fixture
def mock_research_data():
    """Provide mock research data for testing"""
    return {
        "competitors": [
            {
                "name": "Competitor A",
                "price_range": "$50,000 - $70,000",
                "rating": 4.2,
                "strengths": ["Fast delivery", "Good communication"],
                "weaknesses": ["Higher pricing", "Limited expertise"]
            },
            {
                "name": "Competitor B", 
                "price_range": "$45,000 - $65,000",
                "rating": 4.0,
                "strengths": ["Competitive pricing", "Technical expertise"],
                "weaknesses": ["Slower delivery", "Communication issues"]
            }
        ],
        "market_trends": [
            "AI integration in web applications increasing by 35%",
            "Mobile-first development approaches preferred",
            "Cybersecurity concerns driving authentication requirements"
        ],
        "case_studies": [
            {
                "project": "E-commerce Platform for Retail Chain",
                "outcome": "150% increase in online sales",
                "technologies": ["React", "Node.js", "PostgreSQL"]
            }
        ]
    }

@pytest.fixture
def temp_file_cleanup():
    """Cleanup temporary files after tests"""
    temp_files = []
    
    def add_temp_file(filepath):
        temp_files.append(filepath)
    
    yield add_temp_file
    
    # Cleanup
    for filepath in temp_files:
        if os.path.exists(filepath):
            os.remove(filepath)

@pytest.fixture(autouse=True)
def mock_external_apis():
    """Mock external API calls to prevent actual network requests during testing"""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('src.anti_scraping.request_handler.RequestHandler.make_request') as mock_request:
        
        # Default mock responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Mock response content"
        mock_response.json.return_value = {"status": "success", "data": {}}
        
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        mock_request.return_value = mock_response
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'request_handler': mock_request
        }

# Test markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that interact with external APIs"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

# Test data helpers
class TestDataHelper:
    """Helper class for generating test data"""
    
    @staticmethod
    def create_document_data(doc_type: str = "rfp") -> Dict[str, Any]:
        """Create test document data"""
        templates = {
            "rfp": {
                "title": "Request for Proposal - Web Development",
                "content": "We require a comprehensive web application...",
                "requirements": ["web app", "database", "API"]
            },
            "contract": {
                "title": "Development Contract",
                "content": "This contract outlines the terms...",
                "requirements": ["legal compliance", "deliverables"]
            }
        }
        return templates.get(doc_type, templates["rfp"])
    
    @staticmethod
    def create_user_data(role: str = "client") -> Dict[str, Any]:
        """Create test user data"""
        templates = {
            "client": {
                "id": "client_123",
                "name": "John Doe",
                "company": "Acme Corp",
                "email": "john@acme.com"
            },
            "admin": {
                "id": "admin_123", 
                "name": "Admin User",
                "company": "Internal",
                "email": "admin@proposalmaster.com"
            }
        }
        return templates.get(role, templates["client"])

@pytest.fixture
def test_data_helper():
    """Provide test data helper instance"""
    return TestDataHelper()
