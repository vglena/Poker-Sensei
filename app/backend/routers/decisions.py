"""
decisions.py
------------
API router for submitting user decisions and requesting analysis.

Endpoints:
    POST /api/decision/analyze  — Submit a user's action and get analysis (canonical)
    POST /api/decision          — Alias for /decision/analyze (legacy)
    POST /api/analyze           — Stateless analysis without session logging
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, HTTPException
from schemas import DecisionAnalysis, DecisionRequest
from services.agent_bridge import AgentBridge
from services.scenario_service import ScenarioService

router = APIRouter()
_bridge = AgentBridge()
_scenario_service = ScenarioService()


@router.post("/decision/analyze", response_model=DecisionAnalysis, summary="Submit a user action (canonical)")
async def submit_decision_analyze(request: DecisionRequest) -> DecisionAnalysis:
    """Submit the user's action and receive coaching analysis (canonical endpoint)."""
    return await _do_submit(request, log=True)


@router.post("/decision", response_model=DecisionAnalysis, summary="Submit a user action (legacy)")
async def submit_decision(request: DecisionRequest) -> DecisionAnalysis:
    """
    Submit the user's action for a scenario and receive coaching analysis.

    This is the core endpoint of the training loop:
    1. User acted on a scenario
    2. Backend calls the agent to analyze the decision
    3. Agent returns: rating, explanation, best alternative, luck/strategy note, drill

    The decision is logged to the session history.
    """
    return await _do_submit(request, log=True)


async def _do_submit(request: DecisionRequest, log: bool) -> DecisionAnalysis:
    """Shared logic for decision submission endpoints."""
    try:
        scenario_data = request.scenario_data
        if scenario_data is None:
            raise HTTPException(
                status_code=422,
                detail="scenario_data is required. Include the full scenario object from /api/scenario/new.",
            )

        analysis = await _bridge.analyze_decision(
            session_id=request.session_id,
            scenario=scenario_data.model_dump() if hasattr(scenario_data, "model_dump") else dict(scenario_data),
            user_action=request.user_action.value,
            bet_amount=request.bet_amount,
            user_level=request.user_level.value,
            log_decision=log,
        )
        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze", response_model=DecisionAnalysis, summary="Analyze a decision (stateless)")
async def analyze_decision(request: DecisionRequest) -> DecisionAnalysis:
    """
    Analyze a decision without creating a session log entry.
    Useful for replaying hands or testing the analysis engine.
    """
    try:
        if request.scenario_data is None:
            raise HTTPException(status_code=422, detail="scenario_data is required")

        analysis = await _bridge.analyze_decision(
            session_id=request.session_id,
            scenario=request.scenario_data.model_dump() if hasattr(request.scenario_data, "model_dump") else dict(request.scenario_data),
            user_action=request.user_action.value,
            bet_amount=request.bet_amount,
            user_level=request.user_level.value,
            log_decision=False,
        )
        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
