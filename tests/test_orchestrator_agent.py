import pytest
from unittest.mock import MagicMock, AsyncMock

from src.agents.orchestrator_agent import OrchestratorAgent

@pytest.fixture
def orchestrator_agent(mocker):
    """Fixture for the OrchestratorAgent."""
    mocker.patch("src.agents.orchestrator_agent.DocumentProcessor")
    mocker.patch("src.agents.orchestrator_agent.DocumentAnalyzer")
    mocker.patch("src.agents.orchestrator_agent.ContentGenerator")
    mocker.patch("src.agents.orchestrator_agent.SubmissionAgent")
    return OrchestratorAgent()

@pytest.mark.asyncio
async def test_process_workflow_success(orchestrator_agent):
    """Test the end-to-end workflow for a successful case."""
    # Arrange
    file_path = "dummy/path/to/file.txt"

    # Mock the responses from the agents
    orchestrator_agent.document_processor.process.return_value = {"content": "dummy content"}
    orchestrator_agent.document_analyzer.analyze.return_value = {"analysis": "dummy analysis"}
    orchestrator_agent.content_generator.process = AsyncMock(return_value={"status": "success", "content": "dummy proposal"})
    orchestrator_agent.submission_agent.submit.return_value = {"status": "success", "submission_id": "sub_123"}

    # Act
    result = await orchestrator_agent.process(file_path)

    # Assert
    assert result["status"] == "success"
    assert result["proposal"]["content"] == "dummy proposal"
    assert result["analysis"]["analysis"] == "dummy analysis"
    assert result["submission"]["submission_id"] == "sub_123"

    orchestrator_agent.document_processor.process.assert_called_once_with(file_path)
    orchestrator_agent.document_analyzer.analyze.assert_called_once_with({"content": "dummy content"})
    orchestrator_agent.content_generator.process.assert_called_once_with({"analysis": "dummy analysis"})
    orchestrator_agent.submission_agent.submit.assert_called_once_with({"status": "success", "content": "dummy proposal"})

@pytest.mark.asyncio
async def test_process_workflow_document_processing_fails(orchestrator_agent):
    """Test the workflow when document processing fails."""
    # Arrange
    file_path = "dummy/path/to/file.txt"
    orchestrator_agent.document_processor.process.return_value = None

    # Act
    result = await orchestrator_agent.process(file_path)

    # Assert
    assert result["status"] == "error"
    assert result["message"] == "Document processing failed."

@pytest.mark.asyncio
async def test_process_workflow_analysis_fails(orchestrator_agent):
    """Test the workflow when document analysis fails."""
    # Arrange
    file_path = "dummy/path/to/file.txt"
    orchestrator_agent.document_processor.process.return_value = {"content": "dummy content"}
    orchestrator_agent.document_analyzer.analyze.return_value = None

    # Act
    result = await orchestrator_agent.process(file_path)

    # Assert
    assert result["status"] == "error"
    assert result["message"] == "Document analysis failed."

@pytest.mark.asyncio
async def test_process_workflow_content_generation_fails(orchestrator_agent):
    """Test the workflow when content generation fails."""
    # Arrange
    file_path = "dummy/path/to/file.txt"
    orchestrator_agent.document_processor.process.return_value = {"content": "dummy content"}
    orchestrator_agent.document_analyzer.analyze.return_value = {"analysis": "dummy analysis"}
    orchestrator_agent.content_generator.process = AsyncMock(return_value={"status": "error"})

    # Act
    result = await orchestrator_agent.process(file_path)

    # Assert
    assert result["status"] == "error"
    assert result["message"] == "Proposal content generation failed."

@pytest.mark.asyncio
async def test_process_workflow_submission_fails(orchestrator_agent):
    """Test the workflow when submission fails."""
    # Arrange
    file_path = "dummy/path/to/file.txt"
    orchestrator_agent.document_processor.process.return_value = {"content": "dummy content"}
    orchestrator_agent.document_analyzer.analyze.return_value = {"analysis": "dummy analysis"}
    orchestrator_agent.content_generator.process = AsyncMock(return_value={"status": "success", "content": "dummy proposal"})
    orchestrator_agent.submission_agent.submit.return_value = {"status": "error"}

    # Act
    result = await orchestrator_agent.process(file_path)

    # Assert
    assert result["status"] == "error"
    assert result["message"] == "Proposal submission failed."
