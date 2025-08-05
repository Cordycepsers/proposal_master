"""
Client management and assessment routes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ClientProfile(BaseModel):
    """Client profile model."""
    client_id: str
    name: str
    industry: str
    size: str  # 'small', 'medium', 'large', 'enterprise'
    location: str
    key_contacts: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    history: List[Dict[str, Any]]

class ClientAssessment(BaseModel):
    """Client assessment model."""
    assessment_id: str
    client_id: str
    needs_analysis: Dict[str, Any]
    decision_criteria: List[Dict[str, Any]]
    stakeholder_map: List[Dict[str, Any]]
    win_probability: float
    recommended_strategy: Dict[str, Any]

@router.post("/", response_model=ClientProfile)
async def create_client_profile(profile_data: Dict[str, Any]):
    """Create a new client profile."""
    try:
        import uuid
        client_id = str(uuid.uuid4())
        
        profile = ClientProfile(
            client_id=client_id,
            name=profile_data.get("name", ""),
            industry=profile_data.get("industry", ""),
            size=profile_data.get("size", "medium"),
            location=profile_data.get("location", ""),
            key_contacts=profile_data.get("key_contacts", []),
            preferences=profile_data.get("preferences", {}),
            history=[]
        )
        
        logger.info(f"Client profile created: {client_id}")
        return profile
        
    except Exception as e:
        logger.error(f"Client profile creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Profile creation failed: {str(e)}")

@router.post("/{client_id}/assess", response_model=ClientAssessment)
async def assess_client(client_id: str, assessment_data: Dict[str, Any]):
    """Perform client needs assessment."""
    try:
        import uuid
        assessment_id = str(uuid.uuid4())
        
        assessment = ClientAssessment(
            assessment_id=assessment_id,
            client_id=client_id,
            needs_analysis={
                "primary_needs": ["Cost reduction", "Efficiency improvement"],
                "pain_points": ["Legacy system limitations", "Manual processes"],
                "success_criteria": ["ROI > 15%", "Implementation < 6 months"]
            },
            decision_criteria=[
                {"criterion": "Cost", "weight": 0.3, "importance": "high"},
                {"criterion": "Technical capability", "weight": 0.4, "importance": "critical"},
                {"criterion": "Timeline", "weight": 0.3, "importance": "medium"}
            ],
            stakeholder_map=[
                {"name": "CTO", "role": "Technical Decision Maker", "influence": "high", "support_level": "neutral"},
                {"name": "CFO", "role": "Budget Approver", "influence": "critical", "support_level": "supportive"}
            ],
            win_probability=0.65,
            recommended_strategy={
                "approach": "Value-focused with strong technical emphasis",
                "key_messages": ["Proven ROI", "Seamless integration", "Rapid deployment"],
                "risk_areas": ["Budget constraints", "Timeline pressure"]
            }
        )
        
        logger.info(f"Client assessment completed: {assessment_id}")
        return assessment
        
    except Exception as e:
        logger.error(f"Client assessment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@router.get("/")
async def list_clients(limit: int = 50, offset: int = 0):
    """List client profiles."""
    # Mock client list
    return {
        "clients": [
            {
                "client_id": "client-001",
                "name": "TechCorp Industries",
                "industry": "Technology",
                "size": "large",
                "location": "San Francisco, CA"
            }
        ],
        "total_count": 1
    }
