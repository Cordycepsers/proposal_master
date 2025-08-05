# tests/test_research_module.py
import pytest
from unittest.mock import Mock, patch
from src.modules.research.research_module import ResearchModule
from src.anti_scraping.request_handler import RequestHandler

class TestResearchModule:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.researcher = ResearchModule()
        
    @patch('src.anti_scraping.request_handler.RequestHandler.make_request')
    def test_competitor_data_collection(self, mock_request):
        """Test competitor data collection with anti-scraping"""
        # Mock successful competitor data response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <div class="competitor">Company A - $50,000</div>
                <div class="competitor">Company B - $60,000</div>
            </body>
        </html>
        """
        mock_request.return_value = mock_response
        
        competitors = self.researcher.collect_competitor_data("web development", "Technology")
        
        assert isinstance(competitors, list)
        assert len(competitors) > 0
        mock_request.assert_called_once()
        
    @patch('src.anti_scraping.request_handler.RequestHandler.make_request')
    def test_market_trend_analysis(self, mock_request):
        """Test market trend analysis"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <div class="trend">AI integration in web apps increasing</div>
                <div class="trend">Mobile-first development preferred</div>
            </body>
        </html>
        """
        mock_request.return_value = mock_response
        
        trends = self.researcher.analyze_market_trends("web development")
        
        assert isinstance(trends, list)
        assert len(trends) > 0
        
    def test_data_validation(self):
        """Test research data validation"""
        sample_data = [
            {"company": "Company A", "price": "$50,000", "rating": 4.5},
            {"company": "Company B", "price": "$60,000", "rating": 4.2}
        ]
        
        is_valid = self.researcher.validate_research_data(sample_data)
        
        assert isinstance(is_valid, bool)
        assert is_valid == True
        
    @patch('src.anti_scraping.request_handler.RequestHandler.make_request')
    def test_case_study_collection(self, mock_request):
        """Test case study collection"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <div class="case-study">Success story for similar project</div>
            </body>
        </html>
        """
        mock_request.return_value = mock_response
        
        case_studies = self.researcher.collect_case_studies("web development", "Technology")
        
        assert isinstance(case_studies, list)
        assert len(case_studies) > 0
