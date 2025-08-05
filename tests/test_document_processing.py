# tests/test_document_processing.py
import pytest
from unittest.mock import Mock, patch
from src.modules.research.document_processor import DocumentProcessor
from src.anti_scraping.request_handler import RequestHandler

class TestDocumentProcessor:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.processor = DocumentProcessor()
        self.sample_document = {
            "title": "Project Requirements",
            "content": "This project requires development of a web application with user authentication, database integration, and mobile responsiveness. The budget is $50,000 and deadline is 3 months.",
            "requirements": ["web application", "user authentication", "database"],
            "client_info": {"name": "Acme Corp", "industry": "Technology"}
        }
    
    def test_document_parsing(self):
        """Test document parsing functionality"""
        # Test basic parsing
        result = self.processor.parse_document(self.sample_document)
        
        assert result is not None
        assert 'title' in result
        assert 'requirements' in result
        assert 'client_info' in result
        
    def test_requirement_extraction(self):
        """Test requirement extraction from document"""
        requirements = self.processor.extract_requirements(self.sample_document['content'])
        
        assert isinstance(requirements, list)
        assert len(requirements) > 0
        assert 'web application' in requirements
        assert 'user authentication' in requirements
    
    def test_client_info_extraction(self):
        """Test client information extraction"""
        client_data = self.processor.extract_client_info(self.sample_document['content'])
        
        assert isinstance(client_data, dict)
        assert 'name' in client_data
        assert 'industry' in client_data
        assert client_data['name'] == 'Acme Corp'
    
    def test_project_type_classification(self):
        """Test project type classification"""
        project_type = self.processor.classify_project_type(self.sample_document['content'])
        
        assert isinstance(project_type, str)
        assert len(project_type) > 0
    
    @patch('src.anti_scraping.request_handler.RequestHandler.make_request')
    def test_document_analysis_with_anti_scraping(self, mock_request):
        """Test document analysis with anti-scraping measures"""
        # Mock successful request
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Sample competitive analysis data"
        mock_request.return_value = mock_response
        
        result = self.processor.analyze_document_with_research(self.sample_document)
        
        assert result is not None
        assert 'research_data' in result
        mock_request.assert_called_once()
