"""
scenario_service.py
-------------------
Service layer for scenario generation.

Wraps the agent execution script (scenario_engine.py) and converts
its output to the Pydantic schemas used by the API layer.

This is the boundary between the app and the agent system for scenarios.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add agent execution path
AGENT_EXEC = Path(__file__).parent.parent.parent.parent / "agent" / "execution"
sys.path.insert(0, str(AGENT_EXEC))

from scenario_engine import (
    generate_scenario as _engine_generate,
    get_example_scenario,
    Street,
)
from fixtures import get_fixture as _get_fixture, list_fixtures as _list_fixtures, list_fixtures_with_meta as _list_fixtures_with_meta

# Add shared schemas path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
from schemas import (
    PokerScenario,
    PlayerAction,
    BetSizing,
    ActionEnum,
    StreetEnum,
    DifficultyEnum,
)


def _to_schema(raw: Dict[str, Any]) -> PokerScenario:
    """Convert a raw scenario dict to the PokerScenario Pydantic model."""
    action_history = [
        PlayerAction(
            player=a["player"],
            action=ActionEnum(a["action"]),
            amount=a.get("amount"),
        )
        for a in raw.get("action_history", [])
    ]

    bet_sizing_raw = raw.get("bet_sizing", {})
    bet_sizing = BetSizing(
        min_bet=float(bet_sizing_raw.get("min_bet", 1)),
        max_bet=float(bet_sizing_raw.get("max_bet", 1000)),
        common=[float(x) for x in bet_sizing_raw.get("common", [])],
    )

    return PokerScenario(
        scenario_id=str(raw["scenario_id"]),
        street=StreetEnum(raw["street"]),
        hole_cards=raw["hole_cards"],
        community_cards=raw.get("community_cards", []),
        pot_size=float(raw["pot_size"]),
        hero_stack=float(raw["hero_stack"]),
        villain_stack=float(raw["villain_stack"]),
        hero_position=str(raw["hero_position"]),
        villain_position=str(raw["villain_position"]),
        action_history=action_history,
        available_actions=[ActionEnum(a) for a in raw.get("available_actions", [])],
        bet_sizing=bet_sizing,
        difficulty=DifficultyEnum(raw.get("difficulty", "beginner")),
        tags=raw.get("tags", []),
        learning_objective=raw.get("learning_objective"),
    )


class ScenarioService:
    """Generates poker scenarios using the agent execution engine."""

    def generate(
        self,
        difficulty: str = "beginner",
        street: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> PokerScenario:
        """Generate a new scenario and return it as a Pydantic model."""
        street_enum = Street(street) if street else None
        scenario = _engine_generate(
            difficulty=difficulty,
            street=street_enum,
            seed=seed,
        )
        return _to_schema(scenario.to_dict())

    def get_example(self) -> PokerScenario:
        """Return the canonical example scenario."""
        return _to_schema(get_example_scenario())

    def get_fixture(self, name: str) -> PokerScenario:
        """
        Return a named, stable fixture scenario.
        Raises KeyError if the name is not found.
        """
        raw = _get_fixture(name)  # raises KeyError if unknown
        return _to_schema(raw)

    def list_fixtures(self) -> list:
        """Return all available fixture names."""
        return _list_fixtures()

    def list_fixtures_with_meta(self) -> list:
        """Return all fixtures with display metadata (name, label, description, street, difficulty)."""
        return _list_fixtures_with_meta()
