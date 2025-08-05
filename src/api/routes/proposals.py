"""
Proposal generation and management routes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ProposalRequest(BaseModel):
    """Proposal generation request model."""
    rfp_document_id: str
    requirements: List[Dict[str, Any]]
    company_info: Dict[str, Any]
    template_type: str = "standard"  # 'standard', 'technical', 'executive'
    sections: Optional[List[str]] = None
    customizations: Optional[Dict[str, Any]] = None

class ProposalResponse(BaseModel):
    """Proposal generation response model."""
    proposal_id: str
    status: str
    sections: List[Dict[str, Any]]
    executive_summary: str
    compliance_checklist: List[Dict[str, Any]]
    win_themes: List[str]
    word_count: int
    estimated_score: Optional[float] = None

@router.post("/generate", response_model=ProposalResponse)
async def generate_proposal(request: ProposalRequest):
    """Generate a proposal based on RFP requirements."""
    try:
        import uuid
        proposal_id = str(uuid.uuid4())
        
        # Mock proposal generation
        sections = [
            {
                "section_id": "exec_summary",
                "title": "Executive Summary", 
                "content": "Comprehensive executive summary addressing key requirements...",
                "word_count": 500,
                "compliance_score": 0.95
            },
            {
                "section_id": "technical_approach",
                "title": "Technical Approach",
                "content": "Detailed technical solution addressing all requirements...",
                "word_count": 2000,
                "compliance_score": 0.92
            }
        ]
        
        return ProposalResponse(
            proposal_id=proposal_id,
            status="generated",
            sections=sections,
            executive_summary="Executive summary content...",
            compliance_checklist=[
                {"requirement": "Technical specs", "status": "compliant"},
                {"requirement": "Timeline", "status": "compliant"}
            ],
            win_themes=["Innovation", "Proven Experience", "Cost Effectiveness"],
            word_count=2500,
            estimated_score=0.92
        )
        
    except Exception as e:
        logger.error(f"Proposal generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.get("/templates")
async def get_proposal_templates():
    """Get available proposal templates."""
    return {
        "templates": {
            "standard": {
                "name": "Standard Business Proposal",
                "sections": ["Executive Summary", "Company Profile", "Technical Approach", "Management Plan", "Cost Proposal"],
                "typical_length": "15-25 pages"
            },
            "technical": {
                "name": "Technical Solution Proposal", 
                "sections": ["Technical Summary", "Architecture", "Implementation Plan", "Testing Strategy", "Support Model"],
                "typical_length": "20-35 pages"
            },
            "executive": {
                "name": "Executive Summary Focus",
                "sections": ["Executive Summary", "Key Benefits", "Value Proposition", "Investment Summary"],
                "typical_length": "5-10 pages"
            }
        }
    }
