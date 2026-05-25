"""
sessions.py
-----------
API router for session and hand review management.

Endpoints:
    POST /api/hand/review               — Full hand review (canonical)
    POST /api/review                    — Alias for /hand/review (legacy)
    POST /api/session/save              — Save a session summary (canonical)
    POST /api/session                   — Alias for /session/save (legacy)
    GET  /api/session/{session_id}/summary — Get session summary
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, HTTPException
from schemas import (
    HandReview,
    HandReviewRequest,
    SessionSummaryRequest,
    SessionSummaryResponse,
    SessionReport,
)
from services.agent_bridge import AgentBridge

router = APIRouter()
_bridge = AgentBridge()


@router.post("/hand/review", response_model=HandReview, summary="Request full hand review (canonical)")
async def review_hand_canonical(request: HandReviewRequest) -> HandReview:
    """Full hand review — canonical endpoint."""
    return await _do_review(request)


@router.post("/review", response_model=HandReview, summary="Request full hand review (legacy)")
async def review_hand(request: HandReviewRequest) -> HandReview:
    """
    Request a complete review of a played hand.

    The review covers:
    - Key decision point (most impactful moment)
    - Street-by-street grades
    - Luck vs strategy classification
    - Primary lesson and recommended drill
    - Overall grade
    """
    return await _do_review(request)


async def _do_review(request: HandReviewRequest) -> HandReview:
    try:
        if not request.decisions:
            raise HTTPException(status_code=422, detail="decisions list cannot be empty")

        review = await _bridge.review_hand(
            session_id=request.session_id,
            hand_id=request.hand_id,
            decisions=request.decisions,
            showdown_result=request.showdown_result,
        )
        return review

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hand review failed: {str(e)}")


@router.post("/session/save", response_model=SessionSummaryResponse, summary="Save session summary (canonical)")
async def save_session_canonical(request: SessionSummaryRequest) -> SessionSummaryResponse:
    """Save a training session summary — canonical endpoint."""
    return await _do_save_session(request)


@router.post("/session", response_model=SessionSummaryResponse, summary="Save session summary (legacy)")
async def save_session(request: SessionSummaryRequest) -> SessionSummaryResponse:
    """
    Save a training session summary to persistent memory.

    Called at the end of each training session to record:
    - Session stats (decisions, accuracy, average score)
    - Primary lesson learned
    - Notes for the coaching agent
    """
    return await _do_save_session(request)


async def _do_save_session(request: SessionSummaryRequest) -> SessionSummaryResponse:
    try:
        result = await _bridge.save_session(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save session: {str(e)}")


@router.get(
    "/session/{session_id}/summary",
    response_model=SessionReport,
    summary="Get session summary",
)
async def get_session_summary(session_id: str) -> SessionReport:
    """
    Retrieve the rich summary for a specific training session.

    Returns:
    - Total decisions and average score
    - Strongest and weakest decisions
    - Recurring mistake category
    - Recommended next drill
    - Progress note
    """
    try:
        summary = await _bridge.get_session_summary(session_id)
        if summary is None:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found or has no decisions")
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")
