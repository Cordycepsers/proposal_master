# integration_test.py
import pytest
from unittest.mock import Mock, patch
from src.modules.research.proposal_workflow import ProposalWorkflow
from src.anti_scraping.request_handler import RequestHandler

class TestIntegration:
    
    def test_end_to_end_proposal_creation(self):
        """Test complete end-to-end proposal creation"""
        
        # Setup workflow
        workflow = ProposalWorkflow()
        
        # Mock document processing
        with patch.object(workflow, 'process_document') as mock_process:
            mock_process.return_value = {
                "title": "Project Proposal",
                "requirements": ["web application", "database integration"],
                "client_info": {"name": "Acme Corp", "industry": "Technology"}
            }
            
            # Mock content generation
            with patch.object(workflow, 'generate_content') as mock_generate:
                mock_generate.return_value = {
                    "executive_summary": "Executive summary",
                    "problem_statement": "Problem statement",
                    "solution_approach": "Solution approach"
                }
                
                # Test full workflow
                proposal = workflow.create_proposal({
                    "title": "Project Requirements",
                    "content": "Web application with database integration needed"
                })
                
                assert proposal is not None
                assert 'sections' in proposal
                assert len(proposal['sections']) == 3
                
    @patch('src.anti_scraping.request_handler.RequestHandler.make_request')
    def test_research_integration(self, mock_request):
        """Test research integration with anti-scraping"""
        
        # Mock successful research response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <div class="competitor">Company A - $50,000</div>
                <div class="trend">AI integration in web apps increasing</div>
            </body>
        </html>
        """
        mock_request.return_value = mock_response
        
        # Test that research is integrated properly
        workflow = ProposalWorkflow()
        
        with patch.object(workflow, 'process_document') as mock_process:
            mock_process.return_value = {
                "title": "Project Proposal",
                "requirements": ["web application"],
                "client_info": {"name": "Acme Corp"}
            }
            
            proposal = workflow.create_proposal({
                "title": "Project Requirements",
                "content": "Web application needed"
            })
            
            assert proposal is not None
            # Verify research data was collected
            assert 'research_data' in proposal

# Run integration tests
if __name__ == "__main__":
    test = TestIntegration()
    
    print("Running integration tests...")
    
    try:
        test.test_end_to_end_proposal_creation()
        print("✓ End-to-end workflow test passed")
        
        test.test_research_integration()
        print("✓ Research integration test passed")
        
        print("All integration tests passed!")
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        raise
