# tests/test_proposal_workflow.py
import pytest
from unittest.mock import Mock, patch
from src.modules.research.proposal_workflow import ProposalWorkflow
from src.modules.research.document_processor import DocumentProcessor
from src.modules.research.content_generator import ContentGenerator

class TestProposalWorkflow:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.workflow = ProposalWorkflow()
        self.processor = DocumentProcessor()
        self.generator = ContentGenerator()
        
    @patch('src.modules.research.document_processor.DocumentProcessor.parse_document')
    @patch('src.modules.research.content_generator.ContentGenerator.generate_executive_summary')
    @patch('src.modules.research.content_generator.ContentGenerator.generate_problem_statement')
    def test_full_proposal_creation(self, mock_problem, mock_summary, mock_parse):
        """Test complete proposal creation workflow"""
        # Mock responses
        mock_parse.return_value = {
            "title": "Project Proposal",
            "requirements": ["web application"],
            "client_info": {"name": "Acme Corp"}
        }
        
        mock_summary.return_value = "Executive summary content"
        mock_problem.return_value = "Problem statement content"
        
        # Test full workflow
        proposal_data = self.workflow.create_proposal(
            document={
                "title": "Project Requirements",
                "content": "Web application development needed"
            },
            client_profile={"industry": "Technology"}
        )
        
        assert proposal_data is not None
        assert 'sections' in proposal_data
        assert 'executive_summary' in proposal_data['sections']
        assert 'problem_statement' in proposal_data['sections']
        
    def test_proposal_validation(self):
        """Test proposal content validation"""
        sample_proposal = {
            "document_id": "123",
            "sections": {
                "executive_summary": "Executive summary",
                "problem_statement": "Problem statement",
                "solution_approach": "Solution approach"
            },
            "status": "draft"
        }
        
        is_valid = self.workflow.validate_proposal(sample_proposal)
        
        assert isinstance(is_valid, bool)
        assert is_valid == True
        
    @patch('src.modules.research.content_generator.ContentGenerator.generate_content')
    def test_template_based_generation(self, mock_generate):
        """Test template-based content generation"""
        mock_generate.return_value = "Template-based content with placeholders"
        
        template_sections = ["executive_summary", "problem_statement", "solution_approach"]
        
        generated_content = self.workflow.generate_from_template(
            template_sections=template_sections,
            project_requirements=["web application"],
            client_info={"name": "Acme Corp"}
        )
        
        assert isinstance(generated_content, dict)
        assert len(generated_content) == 3
        
    def test_proposal_versioning(self):
        """Test proposal version control"""
        initial_proposal = {
            "version": "1.0",
            "sections": {"executive_summary": "Content"},
            "created_at": "2023-01-01"
        }
        
        updated_proposal = self.workflow.update_proposal_version(initial_proposal)
        
        assert updated_proposal["version"] == "1.1"
