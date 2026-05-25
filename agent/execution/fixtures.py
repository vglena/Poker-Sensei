"""
fixtures.py
-----------
Five stable, named Texas Hold'em training scenarios.

These are hand-crafted for specific learning objectives and remain
constant across runs (unlike generated scenarios). Use them for:
  - Onboarding new users
  - Testing the analysis pipeline
  - Targeted drills for known weaknesses

Fixtures:
    preflop_raise       — Premium hand, raise or fold preflop
    flop_cbet           — Top pair, continuation bet on dry flop
    turn_draw           — Open-ended straight draw, pot odds decision
    river_bluff_catch   — Marginal hand facing a river bet
    value_bet_sizing    — Strong hand, choose the right bet size

Usage:
    from fixtures import FIXTURES
    scenario = FIXTURES["flop_cbet"]
"""

from typing import Dict, Any

# ---------------------------------------------------------------------------
# Canonical fixture definitions
# ---------------------------------------------------------------------------

FIXTURES: Dict[str, Dict[str, Any]] = {

    # ------------------------------------------------------------------
    # 1. PREFLOP RAISE — Hero has A♠K♠, faces open from CO, BTN decision
    # ------------------------------------------------------------------
    "preflop_raise": {
        "scenario_id": "fixture-preflop-raise-001",
        "street": "preflop",
        "hole_cards": ["As", "Ks"],
        "community_cards": [],
        "pot_size": 35.0,         # BB + SB + CO open (25)
        "hero_stack": 965.0,
        "villain_stack": 975.0,
        "hero_position": "BTN",
        "villain_position": "CO",
        "action_history": [
            {"player": "villain (CO)", "action": "raise", "amount": 25.0},
        ],
        "available_actions": ["fold", "call", "raise"],
        "bet_sizing": {
            "min_bet": 50.0,
            "max_bet": 965.0,
            "common": [75.0, 90.0, 115.0],
        },
        "difficulty": "beginner",
        "tags": ["preflop", "3-bet", "premium-hand", "position"],
        "learning_objective": (
            "3-betting in position with premium hands: A-K suited is a clear 3-bet vs a CO open. "
            "Calling is too passive; folding is a major mistake."
        ),
    },

    # ------------------------------------------------------------------
    # 2. FLOP C-BET — Hero has K♥Q♥, flopped top pair on K♦8♣3♠ (dry)
    # ------------------------------------------------------------------
    "flop_cbet": {
        "scenario_id": "fixture-flop-cbet-001",
        "street": "flop",
        "hole_cards": ["Kh", "Qh"],
        "community_cards": ["Kd", "8c", "3s"],
        "pot_size": 55.0,
        "hero_stack": 945.0,
        "villain_stack": 945.0,
        "hero_position": "BTN",
        "villain_position": "BB",
        "action_history": [
            {"player": "hero (BTN)", "action": "raise", "amount": 25.0},
            {"player": "villain (BB)", "action": "call", "amount": 25.0},
            {"player": "villain (BB)", "action": "check", "amount": None},
        ],
        "available_actions": ["check", "bet"],
        "bet_sizing": {
            "min_bet": 10.0,
            "max_bet": 945.0,
            "common": [18.0, 28.0, 41.0],
        },
        "difficulty": "beginner",
        "tags": ["flop", "c-bet", "top-pair", "dry-board", "in-position"],
        "learning_objective": (
            "Continuation betting with top pair on a dry board in position. "
            "K-8-3 rainbow has no flush draws and no connected draws — bet for value and information."
        ),
    },

    # ------------------------------------------------------------------
    # 3. TURN DRAW — Hero has 9♦T♦ with OESD on K♦8♣7♥ board, turn 2♠
    # ------------------------------------------------------------------
    "turn_draw": {
        "scenario_id": "fixture-turn-draw-001",
        "street": "turn",
        "hole_cards": ["9d", "Td"],
        "community_cards": ["Kd", "8c", "7h", "2s"],
        "pot_size": 130.0,
        "hero_stack": 870.0,
        "villain_stack": 870.0,
        "hero_position": "CO",
        "villain_position": "BB",
        "action_history": [
            {"player": "villain (BB)", "action": "check", "amount": None},
            {"player": "hero (CO)", "action": "bet", "amount": 65.0},
            {"player": "villain (BB)", "action": "call", "amount": 65.0},
            {"player": "villain (BB)", "action": "bet", "amount": 80.0},
        ],
        "available_actions": ["fold", "call", "raise"],
        "bet_sizing": {
            "min_bet": 160.0,
            "max_bet": 870.0,
            "common": [160.0, 210.0, 290.0],
        },
        "difficulty": "intermediate",
        "tags": ["turn", "draw", "oesd", "pot-odds", "semi-bluff"],
        "learning_objective": (
            "Calculating pot odds for an open-ended straight draw on the turn. "
            "Hero needs J or 6 to complete the straight (8 outs, ~18% equity). "
            "Pot odds: call 80 into 210 total = ~38% equity needed. Fold is mathematically correct "
            "unless strong implied odds or semi-bluff fold equity justify a raise."
        ),
    },

    # ------------------------------------------------------------------
    # 4. RIVER BLUFF CATCH — Hero has A♣J♦ (top pair), villain bets big
    # ------------------------------------------------------------------
    "river_bluff_catch": {
        "scenario_id": "fixture-river-bluff-catch-001",
        "street": "river",
        "hole_cards": ["Ac", "Jd"],
        "community_cards": ["As", "7c", "3h", "2d", "9s"],
        "pot_size": 280.0,
        "hero_stack": 720.0,
        "villain_stack": 720.0,
        "hero_position": "BB",
        "villain_position": "BTN",
        "action_history": [
            {"player": "hero (BB)", "action": "check", "amount": None},
            {"player": "villain (BTN)", "action": "bet", "amount": 200.0},
        ],
        "available_actions": ["fold", "call"],
        "bet_sizing": {
            "min_bet": 200.0,
            "max_bet": 200.0,
            "common": [200.0],
        },
        "difficulty": "intermediate",
        "tags": ["river", "bluff-catch", "pot-odds", "one-pair", "decision"],
        "learning_objective": (
            "River bluff-catching with one pair. Villain bets 200 into 280 (71% pot). "
            "Hero needs ~41.7% equity to call profitably. "
            "A-J is top pair with second kicker on a board that missed most draws. "
            "This is a marginal but defensible call — villain's range includes bluffs with missed draws."
        ),
    },

    # ------------------------------------------------------------------
    # 5. VALUE BET SIZING — Hero has Q♠Q♣ (set), flop Q♦J♣5♥, villain checks
    # ------------------------------------------------------------------
    "value_bet_sizing": {
        "scenario_id": "fixture-value-bet-sizing-001",
        "street": "flop",
        "hole_cards": ["Qs", "Qc"],
        "community_cards": ["Qd", "Jc", "5h"],
        "pot_size": 80.0,
        "hero_stack": 920.0,
        "villain_stack": 920.0,
        "hero_position": "CO",
        "villain_position": "BB",
        "action_history": [
            {"player": "villain (BB)", "action": "check", "amount": None},
        ],
        "available_actions": ["check", "bet"],
        "bet_sizing": {
            "min_bet": 10.0,
            "max_bet": 920.0,
            "common": [26.0, 40.0, 60.0],
        },
        "difficulty": "intermediate",
        "tags": ["flop", "set", "value-bet", "sizing", "wet-board"],
        "learning_objective": (
            "Bet sizing with a very strong hand on a wet board. "
            "Hero has top set (QQQ). The board Q-J-5 has possible straight draws (KT, T9). "
            "Bet 50–75% pot to build the pot and charge draws. "
            "Avoid slow-playing — connected boards can improve opponent hands quickly."
        ),
    },
}


def get_fixture(name: str) -> Dict[str, Any]:
    """
    Return a fixture scenario dict by name.
    Raises KeyError if the fixture does not exist.
    """
    if name not in FIXTURES:
        raise KeyError(name)
    return FIXTURES[name]


def list_fixtures() -> list:
    """Return all fixture names."""
    return list(FIXTURES.keys())


# Short human-readable labels for UI display.
# Keys match FIXTURES keys; values are (label, short_description) tuples.
FIXTURE_META: Dict[str, Dict[str, str]] = {
    "preflop_raise": {
        "label": "Preflop Raise",
        "description": "A♠K♠ on the BTN vs. a CO open — fold, call, or 3-bet?",
        "street": "preflop",
        "difficulty": "beginner",
    },
    "flop_cbet": {
        "label": "Flop C-Bet",
        "description": "K♥Q♥ top two pair on a dry K♦8♣3♠ board — check or bet?",
        "street": "flop",
        "difficulty": "beginner",
    },
    "turn_draw": {
        "label": "Turn Draw",
        "description": "9♦T♦ open-ended straight draw on the turn — call with correct pot odds?",
        "street": "turn",
        "difficulty": "intermediate",
    },
    "river_bluff_catch": {
        "label": "River Bluff Catch",
        "description": "A♣J♦ top pair facing a large river bet — hero call or fold?",
        "street": "river",
        "difficulty": "intermediate",
    },
    "value_bet_sizing": {
        "label": "Value Bet Sizing",
        "description": "Q♠Q♣ top set on Q♦J♣5♥ — villain checks. How much to bet?",
        "street": "flop",
        "difficulty": "intermediate",
    },
}


def list_fixtures_with_meta() -> list:
    """
    Return all fixtures as a list of dicts with name + metadata.
    Safe to serialize to JSON.
    """
    return [
        {"name": name, **FIXTURE_META.get(name, {"label": name, "description": "", "street": "", "difficulty": ""})}
        for name in FIXTURES
    ]
