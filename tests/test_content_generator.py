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

@pytest.mark.asyncio
async def test_function_calling(content_generator, sample_input_data, mocker):
    """Test the function calling functionality."""
    # Arrange
    mock_gemini_model = mocker.patch('src.modules.proposal.content_generator.genai.GenerativeModel')
    mock_gemini_instance = mock_gemini_model.return_value

    # Mock the first response to be a function call
    mock_function_call = MagicMock()
    mock_function_call.name = "get_client_details"
    mock_function_call.args = {"client_name": "TestCorp"}

    mock_part = MagicMock()
    mock_part.function_call = mock_function_call

    mock_content = MagicMock()
    mock_content.parts = [mock_part]

    mock_candidate = MagicMock()
    mock_candidate.content = mock_content

    mock_response1 = MagicMock()
    mock_response1.candidates = [mock_candidate]

    # Mock the second response to be the final text
    mock_response2 = MagicMock()
    mock_response2.text = "Final response with client details"

    async def mock_generate_content_async(*args, **kwargs):
        if mock_gemini_instance.generate_content_async.call_count == 1:
            return mock_response1
        else:
            return mock_response2

    mock_gemini_instance.generate_content_async = AsyncMock(side_effect=mock_generate_content_async)

    content_generator.model = mock_gemini_instance

    mock_get_client_details = MagicMock(return_value={"name": "TestCorp", "industry": "Software"})
    content_generator.tool_functions["get_client_details"] = mock_get_client_details

    # Act
    result = await content_generator.process(sample_input_data)

    # Assert
    mock_get_client_details.assert_called_once_with(client_name="TestCorp")
    assert "Final response with client details" in result["generated_sections"]["project_overview"]["content"]
