import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.modules.proposal.content_generator import ContentGenerator
import os
import asyncio

@pytest.fixture
def content_generator():
    """Returns a ContentGenerator instance."""
    return ContentGenerator()

@pytest.fixture
def sample_input_data():
    """Provides sample input data for the content generator."""
    return {
        "requirements_analysis": {
            "summary": {"total_requirements": 10, "complexity_score": 6},
            "requirements": {"technical": ["api", "database"]},
            "technical_specifications": {"technologies": ["python", "fastapi"]},
        },
        "client_profile": {"name": "TestCorp", "industry": "Software"},
        "project_specifications": {"title": "New Platform", "timeline": {"duration_months": 6}},
        "content_preferences": {"style": "formal", "sections": ["project_overview", "technical_approach"]},
    }

@pytest.mark.asyncio
async def test_process_with_gemini(content_generator, sample_input_data, mocker):
    """Test the process method with Gemini integration."""
    # Arrange
    mock_gemini_model = mocker.patch('src.modules.proposal.content_generator.genai.GenerativeModel')
    mock_gemini_instance = mock_gemini_model.return_value

    mock_response = MagicMock()
    mock_response.text = "Generated content from Gemini"

    async def mock_generate_content_async(*args, **kwargs):
        return mock_response

    mock_gemini_instance.generate_content_async = AsyncMock(side_effect=mock_generate_content_async)

    content_generator.model = mock_gemini_instance

    # Act
    result = await content_generator.process(sample_input_data)

    # Assert
    assert result["status"] == "success"
    assert "generated_sections" in result
    assert "project_overview" in result["generated_sections"]
    assert "technical_approach" in result["generated_sections"]
    assert result["generated_sections"]["project_overview"]["content"] == "Generated content from Gemini"
    mock_gemini_instance.generate_content_async.assert_called()
    assert mock_gemini_instance.generate_content_async.call_count == 2

@pytest.mark.asyncio
async def test_process_without_gemini(content_generator, sample_input_data):
    """Test the process method without Gemini configured."""
    # Arrange
    content_generator.model = None

    # Act
    result = await content_generator.process(sample_input_data)

    # Assert
    assert result["status"] == "success"
    assert "generated_sections" in result
    assert "project_overview" in result["generated_sections"]
    # Check for fallback content
    assert "This section provides important information" in result["generated_sections"]["project_overview"]["content"]
