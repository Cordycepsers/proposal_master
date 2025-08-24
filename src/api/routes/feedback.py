from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.core import Feedback, Proposal
from ...config.database import get_db_session

router = APIRouter()

class FeedbackCreate(BaseModel):
    proposal_id: int
    rating: int
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    proposal_id: int
    rating: int
    comment: Optional[str] = None

    class Config:
        from_attributes = True

@router.post("/", response_model=FeedbackResponse)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create new feedback for a proposal.
    """
    # Check if proposal exists
    proposal = await db.get(Proposal, feedback_data.proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    new_feedback = Feedback(
        proposal_id=feedback_data.proposal_id,
        rating=feedback_data.rating,
        comment=feedback_data.comment
    )
    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)

    return FeedbackResponse.from_orm(new_feedback)
