"""
scenarios.py
------------
API router for poker scenario requests.

Endpoints:
    GET  /api/scenario          — Get a new training scenario
    GET  /api/scenario/example  — Get the canonical example scenario
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from schemas import PokerScenario, ScenarioRequest, DifficultyEnum, StreetEnum
from services.scenario_service import ScenarioService

router = APIRouter()
_service = ScenarioService()


async def _build_scenario(
    difficulty: DifficultyEnum,
    street: Optional[StreetEnum],
    focus_area: Optional[str],
    seed: Optional[int],
) -> PokerScenario:
    """Shared logic for scenario generation endpoints."""
    try:
        return _service.generate(
            difficulty=difficulty.value,
            street=street.value if street else None,
            seed=seed,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate scenario: {str(e)}")


@router.get("/scenario/new", response_model=PokerScenario, summary="Get a new training scenario")
async def get_scenario_new(
    difficulty: DifficultyEnum = Query(DifficultyEnum.BEGINNER, description="User skill level"),
    street: Optional[StreetEnum] = Query(None, description="Force a specific street (optional)"),
    focus_area: Optional[str] = Query(None, description="Specific skill to focus on"),
    seed: Optional[int] = Query(None, description="Random seed for reproducibility"),
) -> PokerScenario:
    """Generate and return a new poker practice scenario (canonical endpoint)."""
    return await _build_scenario(difficulty, street, focus_area, seed)


@router.get("/scenario", response_model=PokerScenario, summary="Get a new training scenario (legacy)")
async def get_scenario(
    difficulty: DifficultyEnum = Query(DifficultyEnum.BEGINNER, description="User skill level"),
    street: Optional[StreetEnum] = Query(None, description="Force a specific street (optional)"),
    focus_area: Optional[str] = Query(None, description="Specific skill to focus on"),
    seed: Optional[int] = Query(None, description="Random seed for reproducibility"),
) -> PokerScenario:
    """
    Generate and return a new poker practice scenario.

    The scenario is tailored to the requested difficulty level.
    If a street is specified, the scenario will be from that street.
    The learning objective is included but intended to be revealed after the user acts.
    """
    return await _build_scenario(difficulty, street, focus_area, seed)


@router.get("/scenario/fixtures", summary="List all available fixture scenarios")
async def list_fixtures() -> list:
    """
    Return the list of all named fixture scenarios with display metadata.
    Each entry has: name, label, description, street, difficulty.
    """
    return _service.list_fixtures_with_meta()


@router.get("/scenario/fixture/{name}", response_model=PokerScenario, summary="Get a named fixture scenario")
async def get_fixture_scenario(name: str) -> PokerScenario:
    """
    Return a named, stable fixture scenario for testing or specific drills.

    Available fixtures: preflop_raise, flop_cbet, turn_draw, river_bluff_catch, value_bet_sizing
    """
    try:
        return _service.get_fixture(name)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Fixture '{name}' not found. Available: {', '.join(_service.list_fixtures())}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load fixture: {str(e)}")


@router.get("/scenario/example", response_model=PokerScenario, summary="Get the example scenario")
async def get_example_scenario() -> PokerScenario:
    """
    Return the canonical example scenario used for testing and documentation.

    Scenario: Hero has A♥K♦ on a flop of A♣7♥2♣. Villain checks.
    Learning objective: value betting top pair top kicker on a dry board.
    """
    return _service.get_example()
