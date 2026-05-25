"""
schemas.py
----------
Shared Pydantic models for the Poker Training Application.

These schemas are the contract between the frontend and backend.
They define the structure of all data exchanged via the API.

Used by:
    app/backend/routers/     — request/response validation
    app/backend/services/    — service layer type safety
"""

from __future__ import annotations

import re
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import uuid

# ---------------------------------------------------------------------------
# Card code validation
# ---------------------------------------------------------------------------

_CARD_RE = re.compile(r'^[23456789TJQKA][cdhs]$')


def _validate_card(code: str) -> str:
    if not _CARD_RE.match(code):
        raise ValueError(
            f"Invalid card code '{code}'. "
            "Expected rank (23456789TJQKA) + suit (c/d/h/s), e.g. 'Ah', 'Td', 'Ks'."
        )
    return code


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class StreetEnum(str, Enum):
    PREFLOP = "preflop"
    FLOP    = "flop"
    TURN    = "turn"
    RIVER   = "river"


class ActionEnum(str, Enum):
    FOLD  = "fold"
    CHECK = "check"
    CALL  = "call"
    BET   = "bet"
    RAISE = "raise"


class RatingEnum(str, Enum):
    GOOD    = "good"
    OK      = "ok"
    MISTAKE = "mistake"
    BLUNDER = "blunder"


class DifficultyEnum(str, Enum):
    BEGINNER     = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED     = "advanced"
    PRO          = "pro"


class OutcomeClassificationEnum(str, Enum):
    STRATEGY_WIN = "strategy_win"
    STRATEGY_LOSS = "strategy_loss"
    LUCK_WIN     = "luck_win"
    LUCK_LOSS    = "luck_loss"
    MIXED        = "mixed"


# ---------------------------------------------------------------------------
# Card
# ---------------------------------------------------------------------------

class Card(BaseModel):
    """
    A single playing card.
    rank: one of 2 3 4 5 6 7 8 9 T J Q K A
    suit: c (clubs) | d (diamonds) | h (hearts) | s (spades)
    """
    rank: str = Field(..., pattern="^[23456789TJQKA]$")
    suit: str = Field(..., pattern="^[cdhs]$")

    @property
    def code(self) -> str:
        """Compact string representation, e.g. 'Ah'"""
        return f"{self.rank}{self.suit}"

    @classmethod
    def from_code(cls, code: str) -> "Card":
        if len(code) != 2:
            raise ValueError(f"Invalid card code: '{code}'")
        return cls(rank=code[0].upper(), suit=code[1].lower())


# ---------------------------------------------------------------------------
# Player action
# ---------------------------------------------------------------------------

class PlayerAction(BaseModel):
    """A single action taken by a player during a hand."""
    player: str
    action: ActionEnum
    amount: Optional[float] = None


# ---------------------------------------------------------------------------
# Bet sizing
# ---------------------------------------------------------------------------

class BetSizing(BaseModel):
    """Bet sizing options for the current decision."""
    min_bet: float
    max_bet: float
    common: List[float] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Poker scenario
# ---------------------------------------------------------------------------

class PokerScenario(BaseModel):
    """
    A structured poker training scenario.
    Sent from the backend to the frontend when a new hand starts.
    """
    scenario_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    street: StreetEnum
    hole_cards: List[str] = Field(..., min_length=2, max_length=2)
    community_cards: List[str] = Field(default_factory=list, max_length=5)
    pot_size: float = Field(..., gt=0)
    hero_stack: float = Field(..., gt=0)
    villain_stack: float = Field(..., gt=0)
    hero_position: str
    villain_position: str
    action_history: List[PlayerAction] = Field(default_factory=list)
    available_actions: List[ActionEnum]
    bet_sizing: BetSizing
    difficulty: DifficultyEnum = DifficultyEnum.BEGINNER
    tags: List[str] = Field(default_factory=list)

    # Hidden from user until after they act
    learning_objective: Optional[str] = None

    @field_validator('hole_cards', 'community_cards', mode='before')
    @classmethod
    def validate_card_codes(cls, v: List[str]) -> List[str]:
        return [_validate_card(str(c)) for c in v]

    @field_validator('available_actions')
    @classmethod
    def validate_actions_not_empty(cls, v: List[ActionEnum]) -> List[ActionEnum]:
        if not v:
            raise ValueError("available_actions cannot be empty")
        return v


# ---------------------------------------------------------------------------
# Decision analysis
# ---------------------------------------------------------------------------

class DecisionAnalysis(BaseModel):
    """
    The coaching analysis of a single user decision.
    Returned by the agent after the user submits their action.
    """
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    user_action: ActionEnum
    bet_amount: Optional[float] = None

    # Rating
    rating: RatingEnum
    rating_score: int = Field(..., ge=1, le=10)

    # Coaching content
    hand_strength: Optional[str] = None
    position_note: Optional[str] = None
    explanation: str
    best_alternative: str
    recommended_sizing: Optional[str] = None
    risk_analysis: str
    luck_vs_strategy: str
    key_concept: Optional[str] = None
    mistake_category: Optional[str] = None   # e.g. "passive_play", "over_bluff", "sizing_error"
    recommended_drill: str

    # What the learning objective was (revealed post-action)
    learning_objective: Optional[str] = None


# ---------------------------------------------------------------------------
# Hand review
# ---------------------------------------------------------------------------

class StreetGrade(BaseModel):
    """Performance grade for a single street."""
    rating: RatingEnum
    score: int = Field(..., ge=1, le=10)
    note: str


class KeyDecision(BaseModel):
    """The most important decision point in the hand."""
    street: StreetEnum
    hero_action: str
    optimal_action: str
    sizing_recommendation: Optional[str] = None
    explanation: str


class HandReview(BaseModel):
    """
    A full post-hand review covering all streets.
    Returned after a complete hand is played.
    """
    hand_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    outcome: str                        # "win" | "loss" | "fold"
    outcome_classification: OutcomeClassificationEnum
    key_decision: KeyDecision
    street_grades: Dict[str, StreetGrade]
    luck_vs_strategy: str
    primary_lesson: str
    recommended_drill: str
    overall_grade: RatingEnum
    overall_score: int = Field(..., ge=1, le=10)


# ---------------------------------------------------------------------------
# User profile
# ---------------------------------------------------------------------------

class UserProfile(BaseModel):
    """
    The user's profile and coaching configuration.
    Persisted in memory/user_profile.md (v1) or a database (future).
    """
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    display_name: str = "Player"
    level: DifficultyEnum = DifficultyEnum.BEGINNER
    goal: str = "general-improvement"
    preferred_format: str = "cash"
    feedback_tone: str = "direct"       # direct | gentle | technical

    # Session stats
    total_sessions: int = 0
    total_decisions: int = 0
    average_score: float = 0.0
    accuracy_pct: float = 0.0


# ---------------------------------------------------------------------------
# API request / response models
# ---------------------------------------------------------------------------

class ScenarioRequest(BaseModel):
    """Request a new practice scenario."""
    user_level: DifficultyEnum = DifficultyEnum.BEGINNER
    street_preference: Optional[StreetEnum] = None
    focus_area: Optional[str] = None
    seed: Optional[int] = None


class DecisionRequest(BaseModel):
    """Submit a user's action for a scenario."""
    session_id: str
    scenario_id: str
    user_action: ActionEnum
    bet_amount: Optional[float] = None
    user_level: DifficultyEnum = DifficultyEnum.BEGINNER
    scenario_data: Optional[PokerScenario] = None   # Full scenario (required for stateless mode)

    @field_validator('bet_amount')
    @classmethod
    def validate_bet_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("bet_amount must be positive")
        return v


class HandReviewRequest(BaseModel):
    """Request a full hand review after the hand is complete."""
    session_id: str
    hand_id: str
    decisions: List[DecisionRequest]
    showdown_result: Optional[Dict[str, Any]] = None


class SessionSummaryRequest(BaseModel):
    """Save a session summary after training ends."""
    session_id: str
    user_id: str
    total_decisions: int = Field(..., ge=0)
    hands_played: int = Field(default=0, ge=0)
    average_score: float = Field(..., ge=0.0, le=10.0)
    accuracy_pct: float = Field(..., ge=0.0, le=100.0)
    primary_lesson: Optional[str] = None
    notes: Optional[str] = None


class SessionSummaryResponse(BaseModel):
    """Confirmation that a session was saved."""
    session_id: str
    saved: bool
    message: str


class SessionReport(BaseModel):
    """
    Rich end-of-session report generated from decision logs.
    Returned by GET /api/session/{id}/summary.
    """
    session_id: str
    total_decisions: int
    average_score: float
    accuracy_pct: float
    strongest_decision: Optional[Dict[str, Any]] = None   # Highest-scoring decision
    weakest_decision: Optional[Dict[str, Any]] = None     # Lowest-scoring decision
    recurring_mistake: Optional[str] = None               # Most common mistake category
    recommended_drill: Optional[str] = None
    progress_note: str = ""
    streets_played: Dict[str, int] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Example instances (for testing and documentation)
# ---------------------------------------------------------------------------

EXAMPLE_SCENARIO = PokerScenario(
    scenario_id="example-001",
    street=StreetEnum.FLOP,
    hole_cards=["Ah", "Kd"],
    community_cards=["Ac", "7h", "2c"],
    pot_size=100.0,
    hero_stack=900.0,
    villain_stack=900.0,
    hero_position="BTN",
    villain_position="BB",
    action_history=[PlayerAction(player="villain (BB)", action=ActionEnum.CHECK)],
    available_actions=[ActionEnum.CHECK, ActionEnum.BET],
    bet_sizing=BetSizing(min_bet=25.0, max_bet=900.0, common=[33.0, 50.0, 75.0]),
    difficulty=DifficultyEnum.BEGINNER,
    tags=["flop", "value-bet", "top-pair", "dry-board", "in-position"],
    learning_objective="value betting top pair top kicker on a dry board in position",
)

EXAMPLE_ANALYSIS = DecisionAnalysis(
    decision_id="analysis-001",
    scenario_id="example-001",
    user_action=ActionEnum.CHECK,
    bet_amount=None,
    rating=RatingEnum.MISTAKE,
    rating_score=4,
    hand_strength="top pair top kicker",
    position_note="Hero is in position (BTN). Acting last gives information and control.",
    explanation=(
        "You have top pair with the best kicker — A-K on an A-7-2 board. "
        "This is one of the strongest hands you can have here. "
        "When you check back, you miss value from worse aces, sevens, and any draws. "
        "The board is dry (no flush draw, no realistic straight draws), so there is no "
        "urgency to protect your hand. The main reason to bet is simply: you are winning, "
        "and you should charge your opponent to stay in."
    ),
    best_alternative="Bet 50% of the pot (50 chips)",
    recommended_sizing="33–66% pot (33–66 chips)",
    risk_analysis=(
        "The main risk of betting is running into a slow-played set (222, 777, AA). "
        "However, sets are rare. The far bigger risk is checking and giving a free card "
        "that beats you, or simply missing value by not growing the pot."
    ),
    luck_vs_strategy=(
        "Strategy. This decision is fully within your control. "
        "Regardless of what card comes next, betting here was the correct play."
    ),
    key_concept="value betting",
    recommended_drill="Practice betting top pair in position on dry boards. Focus on bet sizing: 33–66% pot.",
    learning_objective="value betting top pair top kicker on a dry board in position",
)
