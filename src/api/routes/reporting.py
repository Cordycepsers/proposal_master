from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...models.core import Feedback
from ...config.database import get_db_session
from ...modules.reporting.feedback_analyzer import FeedbackAnalyzer

router = APIRouter()

@router.get("/feedback")
async def get_feedback_report(db: AsyncSession = Depends(get_db_session)):
    """
    Get a report of user feedback.
    """
    feedback_list = (await db.execute(select(Feedback))).scalars().all()

    analyzer = FeedbackAnalyzer()
    analysis = analyzer.analyze_feedback(feedback_list)

    return analysis
