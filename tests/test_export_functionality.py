# tests/test_export_functionality.py
import pytest
from unittest.mock import Mock, patch
from src.modules.research.export_manager import ExportManager
import os

class TestExportFunctionality:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.export_manager = ExportManager()
        
    @patch('src.modules.research.export_manager.ExportManager.convert_to_pdf')
    def test_pdf_export(self, mock_convert):
        """Test PDF export functionality"""
        mock_convert.return_value = b"pdf_content"
        
        pdf_content = self.export_manager.export_to_pdf(
            proposal_data={
                "sections": {
                    "executive_summary": "Executive summary",
                    "problem_statement": "Problem statement"
                }
            },
            filename="test_proposal.pdf"
        )
        
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        
    @patch('src.modules.research.export_manager.ExportManager.convert_to_word')
    def test_word_export(self, mock_convert):
        """Test Word export functionality"""
        mock_convert.return_value = b"word_content"
        
        word_content = self.export_manager.export_to_word(
            proposal_data={
                "sections": {
                    "executive_summary": "Executive summary",
                    "problem_statement": "Problem statement"
                }
            },
            filename="test_proposal.docx"
        )
        
        assert isinstance(word_content, bytes)
        assert len(word_content) > 0
        
    def test_file_format_validation(self):
        """Test file format validation"""
        valid_formats = ["pdf", "docx", "html"]
        invalid_formats = ["txt", "xls", "ppt"]
        
        for fmt in valid_formats:
            is_valid = self.export_manager.validate_file_format(fmt)
            assert is_valid == True
            
        for fmt in invalid_formats:
            is_valid = self.export_manager.validate_file_format(fmt)
            assert is_valid == False
            
    def test_export_with_branding(self):
        """Test export with company branding"""
        # Test that export includes branding elements
        proposal_data = {
            "sections": {"executive_summary": "Executive summary"},
            "branding": {
                "company_name": "Acme Corp",
                "logo_url": "https://example.com/logo.png"
            }
        }
        
        pdf_content = self.export_manager.export_with_branding(
            proposal_data=proposal_data,
            format="pdf"
        )
        
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
