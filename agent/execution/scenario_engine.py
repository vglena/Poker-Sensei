"""
scenario_engine.py
------------------
Deterministic module for generating structured Texas Hold'em practice scenarios.

The AI agent can request scenarios from this engine. The engine produces valid,
structured outputs with realistic card distributions and action histories.

All randomness is seeded and reproducible.

Public API:
    generate_scenario(difficulty, street, seed)     -> PokerScenario
    generate_scenario_batch(count, difficulty, seed) -> List[PokerScenario]
    get_example_scenario()                           -> dict
"""

import random
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Street(str, Enum):
    PREFLOP = "preflop"
    FLOP    = "flop"
    TURN    = "turn"
    RIVER   = "river"


class Position(str, Enum):
    UTG  = "UTG"
    HJ   = "HJ"
    CO   = "CO"
    BTN  = "BTN"
    SB   = "SB"
    BB   = "BB"


class ActionType(str, Enum):
    FOLD  = "fold"
    CHECK = "check"
    CALL  = "call"
    BET   = "bet"
    RAISE = "raise"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PlayerAction:
    player: str
    action: ActionType
    amount: Optional[float] = None


@dataclass
class BetSizing:
    min_bet: float
    max_bet: float
    common: List[float]  # Suggested sizes in chips


@dataclass
class PokerScenario:
    scenario_id: str
    street: Street
    hole_cards: List[str]
    community_cards: List[str]
    pot_size: float
    hero_stack: float
    villain_stack: float
    hero_position: Position
    villain_position: Position
    action_history: List[PlayerAction]
    available_actions: List[ActionType]
    bet_sizing: BetSizing
    learning_objective: str
    difficulty: str
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dictionary (JSON-compatible)."""
        d = asdict(self)
        # Convert enums to string values
        d["street"] = self.street.value
        d["hero_position"] = self.hero_position.value
        d["villain_position"] = self.villain_position.value
        d["available_actions"] = [a.value for a in self.available_actions]
        d["action_history"] = [
            {"player": a.player, "action": a.action.value, "amount": a.amount}
            for a in self.action_history
        ]
        return d


# ---------------------------------------------------------------------------
# Card deck utilities
# ---------------------------------------------------------------------------

_DECK = [
    f"{rank}{suit}"
    for rank in "23456789TJQKA"
    for suit in "cdhs"
]


def _deal(n: int, excluded: Optional[List[str]] = None) -> List[str]:
    """Deal n unique cards, excluding already-used cards."""
    available = [c for c in _DECK if c not in (excluded or [])]
    if n > len(available):
        raise ValueError(f"Cannot deal {n} cards; only {len(available)} available")
    return random.sample(available, n)


def _is_dry_board(cards: List[str]) -> bool:
    """True if the board has no flush draw (all different suits) and no straight draw."""
    suits = [c[1] for c in cards]
    if len(set(suits)) < len(cards):
        return False
    vals = sorted({"23456789TJQKA".index(c[0]) for c in cards})
    if len(vals) >= 3 and vals[-1] - vals[0] <= 4:
        return False
    return True


def _bet_sizes(pot: float, stack: float) -> BetSizing:
    common = [round(pot * r) for r in [0.33, 0.50, 0.75]]
    common = [max(1.0, min(s, stack)) for s in common]
    return BetSizing(
        min_bet=max(1.0, round(pot * 0.20)),
        max_bet=stack,
        common=common,
    )


# ---------------------------------------------------------------------------
# Scenario generators by street
# ---------------------------------------------------------------------------

_OBJECTIVES: Dict[str, Dict[str, str]] = {
    "flop": {
        "beginner":     "value betting top pair on the flop",
        "intermediate": "choosing between betting and checking on the flop based on board texture",
        "advanced":     "constructing a flop betting range with value and bluffs",
        "pro":          "solver-aligned flop strategy: bet frequency and sizing by board type",
    },
    "preflop": {
        "beginner":     "basic preflop hand selection and understanding position",
        "intermediate": "3-betting vs calling based on position and hand strength",
        "advanced":     "constructing a preflop 3-bet range with value and bluffs",
        "pro":          "GTO preflop ranges vs exploitative adjustments",
    },
    "turn": {
        "beginner":     "deciding whether to continue betting or check on the turn",
        "intermediate": "barrel sizing and semi-bluffing on the turn",
        "advanced":     "range-based turn strategy with draws and made hands",
        "pro":          "turn polarization and mixed-frequency decisions",
    },
    "river": {
        "beginner":     "calling vs folding on the river using pot odds",
        "intermediate": "identifying bluff-catching spots on the river",
        "advanced":     "value betting vs bluffing on the river based on ranges",
        "pro":          "MDF, optimal river defense frequency, and bet sizing",
    },
}

_POSITIONS = list(Position)


def _opposite_position(pos: Position) -> Position:
    """Return a reasonable opposing position."""
    mapping = {
        Position.BTN: Position.BB,
        Position.CO:  Position.BB,
        Position.HJ:  Position.BB,
        Position.SB:  Position.BTN,
        Position.BB:  Position.BTN,
        Position.UTG: Position.BTN,
    }
    return mapping.get(pos, Position.BB)


def _generate_flop_scenario(difficulty: str) -> PokerScenario:
    hero_pos = random.choice([Position.BTN, Position.CO, Position.HJ, Position.BB, Position.SB])
    villain_pos = _opposite_position(hero_pos)

    hole = _deal(2)
    community = _deal(3, excluded=hole)
    pot = float(random.choice([60, 80, 100, 120, 150]))
    stack = float(random.randint(400, 1000))

    action_history = [PlayerAction(player=f"villain ({villain_pos.value})", action=ActionType.CHECK)]
    available_actions = [ActionType.CHECK, ActionType.BET]
    bet_sizing = _bet_sizes(pot, stack)

    tags = ["flop", "heads-up"]
    if _is_dry_board(community):
        tags.append("dry-board")
    else:
        tags.append("wet-board")
    if hero_pos in [Position.BTN, Position.CO, Position.HJ]:
        tags.append("in-position")
    else:
        tags.append("out-of-position")

    return PokerScenario(
        scenario_id=str(uuid.uuid4()),
        street=Street.FLOP,
        hole_cards=hole,
        community_cards=community,
        pot_size=pot,
        hero_stack=stack,
        villain_stack=stack,
        hero_position=hero_pos,
        villain_position=villain_pos,
        action_history=action_history,
        available_actions=available_actions,
        bet_sizing=bet_sizing,
        learning_objective=_OBJECTIVES["flop"].get(difficulty, _OBJECTIVES["flop"]["beginner"]),
        difficulty=difficulty,
        tags=tags,
    )


def _generate_preflop_scenario(difficulty: str) -> PokerScenario:
    hero_pos = random.choice(_POSITIONS)
    raiser_pos = random.choice([Position.UTG, Position.HJ, Position.CO, Position.BTN])
    if raiser_pos == hero_pos:
        raiser_pos = Position.UTG

    hole = _deal(2)
    bb_size = 2.0
    raise_size = float(random.choice([2.5, 3.0, 3.5, 4.0])) * bb_size
    pot = bb_size * 1.5 + raise_size  # SB + BB + raise
    stack = float(random.randint(80, 200)) * bb_size  # in chips

    action_history = [
        PlayerAction(
            player=f"villain ({raiser_pos.value})",
            action=ActionType.RAISE,
            amount=raise_size,
        )
    ]
    available_actions = [ActionType.FOLD, ActionType.CALL, ActionType.RAISE]
    bet_sizing = BetSizing(
        min_bet=raise_size * 2.5,
        max_bet=stack,
        common=[round(raise_size * 3), round(raise_size * 4)],
    )

    return PokerScenario(
        scenario_id=str(uuid.uuid4()),
        street=Street.PREFLOP,
        hole_cards=hole,
        community_cards=[],
        pot_size=pot,
        hero_stack=stack,
        villain_stack=stack,
        hero_position=hero_pos,
        villain_position=raiser_pos,
        action_history=action_history,
        available_actions=available_actions,
        bet_sizing=bet_sizing,
        learning_objective=_OBJECTIVES["preflop"].get(difficulty, _OBJECTIVES["preflop"]["beginner"]),
        difficulty=difficulty,
        tags=["preflop", "facing-raise"],
    )


def _generate_turn_scenario(difficulty: str) -> PokerScenario:
    hero_pos = random.choice([Position.BTN, Position.CO, Position.BB, Position.SB])
    villain_pos = _opposite_position(hero_pos)

    hole = _deal(2)
    community = _deal(4, excluded=hole)
    pot = float(random.choice([100, 150, 200, 250]))
    stack = float(random.randint(300, 900))

    # Villain checks, hero acts
    action_history = [PlayerAction(player=f"villain ({villain_pos.value})", action=ActionType.CHECK)]
    available_actions = [ActionType.CHECK, ActionType.BET]
    bet_sizing = _bet_sizes(pot, stack)

    return PokerScenario(
        scenario_id=str(uuid.uuid4()),
        street=Street.TURN,
        hole_cards=hole,
        community_cards=community,
        pot_size=pot,
        hero_stack=stack,
        villain_stack=stack,
        hero_position=hero_pos,
        villain_position=villain_pos,
        action_history=action_history,
        available_actions=available_actions,
        bet_sizing=bet_sizing,
        learning_objective=_OBJECTIVES["turn"].get(difficulty, _OBJECTIVES["turn"]["beginner"]),
        difficulty=difficulty,
        tags=["turn", "heads-up"],
    )


def _generate_river_scenario(difficulty: str) -> PokerScenario:
    hero_pos = random.choice([Position.BTN, Position.CO, Position.BB])
    villain_pos = _opposite_position(hero_pos)

    hole = _deal(2)
    community = _deal(5, excluded=hole)
    pot = float(random.choice([150, 200, 300, 400]))
    stack = float(random.randint(200, 800))

    # Villain bets into hero
    villain_bet = round(pot * random.choice([0.40, 0.50, 0.65, 0.75, 1.0]))
    action_history = [
        PlayerAction(
            player=f"villain ({villain_pos.value})",
            action=ActionType.BET,
            amount=float(villain_bet),
        )
    ]
    available_actions = [ActionType.FOLD, ActionType.CALL, ActionType.RAISE]
    bet_sizing = BetSizing(
        min_bet=villain_bet * 2.2,
        max_bet=stack,
        common=[round(villain_bet * 3), round(villain_bet * 4)],
    )

    return PokerScenario(
        scenario_id=str(uuid.uuid4()),
        street=Street.RIVER,
        hole_cards=hole,
        community_cards=community,
        pot_size=pot,
        hero_stack=stack,
        villain_stack=stack,
        hero_position=hero_pos,
        villain_position=villain_pos,
        action_history=action_history,
        available_actions=available_actions,
        bet_sizing=bet_sizing,
        learning_objective=_OBJECTIVES["river"].get(difficulty, _OBJECTIVES["river"]["beginner"]),
        difficulty=difficulty,
        tags=["river", "facing-bet", "heads-up"],
    )


# ---------------------------------------------------------------------------
# Generator dispatch
# ---------------------------------------------------------------------------

_GENERATORS = {
    Street.PREFLOP: _generate_preflop_scenario,
    Street.FLOP:    _generate_flop_scenario,
    Street.TURN:    _generate_turn_scenario,
    Street.RIVER:   _generate_river_scenario,
}

_STREET_WEIGHTS: Dict[str, List[float]] = {
    "beginner":     [0.30, 0.50, 0.00, 0.20],  # preflop, flop, turn, river
    "intermediate": [0.20, 0.40, 0.25, 0.15],
    "advanced":     [0.15, 0.30, 0.30, 0.25],
    "pro":          [0.10, 0.25, 0.35, 0.30],
}
_STREET_ORDER = [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]


def _random_street(difficulty: str) -> Street:
    weights = _STREET_WEIGHTS.get(difficulty, _STREET_WEIGHTS["beginner"])
    return random.choices(_STREET_ORDER, weights=weights, k=1)[0]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_scenario(
    difficulty: str = "beginner",
    street: Optional[Street] = None,
    seed: Optional[int] = None,
) -> PokerScenario:
    """
    Generate one structured poker practice scenario.

    Args:
        difficulty: "beginner" | "intermediate" | "advanced" | "pro"
        street:     Force a specific street (random if None)
        seed:       Random seed for reproducibility

    Returns:
        PokerScenario dataclass
    """
    if difficulty not in ("beginner", "intermediate", "advanced", "pro"):
        raise ValueError(f"Invalid difficulty: '{difficulty}'")

    if seed is not None:
        random.seed(seed)

    chosen_street = street if street is not None else _random_street(difficulty)
    generator = _GENERATORS[chosen_street]
    return generator(difficulty)


def generate_scenario_batch(
    count: int,
    difficulty: str = "beginner",
    seed: Optional[int] = None,
) -> List[PokerScenario]:
    """Generate multiple scenarios for a training session."""
    if seed is not None:
        random.seed(seed)
    return [generate_scenario(difficulty) for _ in range(count)]


def get_example_scenario() -> Dict[str, Any]:
    """
    Return a hardcoded example scenario for testing and documentation.
    This is the canonical example used throughout the system.
    """
    return {
        "scenario_id": "example-001",
        "street": "flop",
        "hole_cards": ["Ah", "Kd"],
        "community_cards": ["Ac", "7h", "2c"],
        "pot_size": 100,
        "hero_stack": 900,
        "villain_stack": 900,
        "hero_position": "BTN",
        "villain_position": "BB",
        "action_history": [
            {"player": "villain (BB)", "action": "check", "amount": None}
        ],
        "available_actions": ["check", "bet"],
        "bet_sizing": {
            "min_bet": 25,
            "max_bet": 900,
            "common": [33, 50, 75],
        },
        "learning_objective": "value betting top pair top kicker on a dry board in position",
        "difficulty": "beginner",
        "tags": ["flop", "value-bet", "top-pair", "dry-board", "in-position"],
    }


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    # Generate a beginner flop scenario
    scenario = generate_scenario(difficulty="beginner", street=Street.FLOP, seed=42)
    print("=== Generated Scenario ===")
    print(json.dumps(scenario.to_dict(), indent=2, default=str))

    print("\n=== Example Scenario ===")
    print(json.dumps(get_example_scenario(), indent=2))
