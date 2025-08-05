# tests/test_ai_content_generation.py
import pytest
from unittest.mock import Mock, patch
from src.modules.research.content_generator import ContentGenerator

class TestContentGenerator:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.generator = ContentGenerator()
        
    @patch('src.modules.research.content_generator.ContentGenerator.generate_content')
    def test_executive_summary_generation(self, mock_generate):
        """Test executive summary generation"""
        mock_generate.return_value = "Executive summary content for project"
        
        summary = self.generator.generate_executive_summary(
            project_requirements=["web application", "database integration"],
            client_name="Acme Corp"
        )
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "Acme Corp" in summary
        
    @patch('src.modules.research.content_generator.ContentGenerator.generate_content')
    def test_problem_statement_generation(self, mock_generate):
        """Test problem statement generation"""
        mock_generate.return_value = "Problem statement describing challenges"
        
        problem = self.generator.generate_problem_statement(
            project_requirements=["web application", "database integration"],
            client_context="Technology company"
        )
        
        assert isinstance(problem, str)
        assert len(problem) > 0
        
    @patch('src.modules.research.content_generator.ContentGenerator.generate_content')
    def test_solution_approach_generation(self, mock_generate):
        """Test solution approach generation"""
        mock_generate.return_value = "Solution approach with technical details"
        
        solution = self.generator.generate_solution_approach(
            requirements=["web application", "database integration"],
            project_type="web development"
        )
        
        assert isinstance(solution, str)
        assert len(solution) > 0
        
    def test_content_quality_validation(self):
        """Test content quality validation"""
        sample_content = "This is a well-written proposal section with proper formatting and professional language."
        
        is_valid = self.generator.validate_content_quality(sample_content)
        
        assert isinstance(is_valid, bool)
        assert is_valid == True  # Assuming valid content
        
    @patch('src.modules.research.content_generator.ContentGenerator.generate_content')
    def test_personalized_content_generation(self, mock_generate):
        """Test personalized content based on client profile"""
        mock_generate.return_value = "Personalized content for technology company"
        
        personalization = self.generator.generate_personalized_content(
            client_profile={"industry": "Technology", "size": "Large"},
            project_requirements=["web application"]
        )
        
        assert isinstance(personalization, str)
        assert len(personalization) > 0
