import pytest
from src.modules.proposal.content_generator import ContentGenerator

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
async def test_process_success(content_generator, sample_input_data):
    """Test the process method for successful content generation."""
    result = await content_generator.process(sample_input_data)

    assert result["status"] == "success"
    assert "proposal_id" in result
    assert "generated_sections" in result
    assert "project_overview" in result["generated_sections"]
    assert "technical_approach" in result["generated_sections"]
    assert "proposal_structure" in result
    assert "executive_summary" in result
    assert "content_metrics" in result
    assert "content_recommendations" in result

    # Check some content details
    assert "TestCorp" in result["generated_sections"]["project_overview"]["content"]
    assert "New Platform" in result["generated_sections"]["project_overview"]["content"]
    assert "python" in result["generated_sections"]["technical_approach"]["content"]
    assert "fastapi" in result["generated_sections"]["technical_approach"]["content"]

@pytest.mark.asyncio
async def test_process_missing_requirements(content_generator, sample_input_data):
    """Test the process method when requirements_analysis is missing."""
    del sample_input_data["requirements_analysis"]
    result = await content_generator.process(sample_input_data)

    assert result["status"] == "error"
    assert "Requirements analysis is required" in result["error"]

@pytest.mark.asyncio
async def test_get_statistics(content_generator, sample_input_data):
    """Test the get_statistics method."""
    initial_stats = content_generator.get_statistics()
    assert initial_stats["proposals_generated"] == 0

    await content_generator.process(sample_input_data)

    updated_stats = content_generator.get_statistics()
    assert updated_stats["proposals_generated"] == 1
    assert updated_stats["sections_created"] == 2
    assert updated_stats["avg_word_count"] > 0
