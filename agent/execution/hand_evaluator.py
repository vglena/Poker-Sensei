"""
hand_evaluator.py
-----------------
Deterministic poker hand strength evaluator.

Evaluates the best 5-card hand from any combination of hole cards + community cards.
This module uses pure combinatorial logic — no AI reasoning, no external libraries.

It can be replaced later with a stronger poker engine (e.g., Cactus Kev, PokerKit).

Public API:
    parse_cards(card_strings)       -> List[Card]
    best_hand(hole, community)      -> HandResult
    hand_strength_label(result)     -> str
    compare_hands(hand_a, hand_b)   -> int  (-1, 0, 1)
"""

from itertools import combinations
from typing import List, Tuple, Dict
from dataclasses import dataclass
from enum import IntEnum


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RANKS = "23456789TJQKA"
SUITS = "cdhs"  # clubs, diamonds, hearts, spades
RANK_VALUES: Dict[str, int] = {r: i for i, r in enumerate(RANKS, start=2)}


# ---------------------------------------------------------------------------
# Card
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Card:
    """Immutable representation of a single playing card."""
    rank: str   # One of: 2 3 4 5 6 7 8 9 T J Q K A
    suit: str   # One of: c d h s

    def __post_init__(self) -> None:
        if self.rank not in RANKS:
            raise ValueError(f"Invalid rank '{self.rank}'. Must be one of: {RANKS}")
        if self.suit not in SUITS:
            raise ValueError(f"Invalid suit '{self.suit}'. Must be one of: {SUITS}")

    @property
    def value(self) -> int:
        """Numeric value of the rank (2=2, Ace=14)."""
        return RANK_VALUES[self.rank]

    @classmethod
    def from_string(cls, s: str) -> "Card":
        """
        Parse a card from a 2-character string.
        Examples: 'Ah' -> Ace of hearts, 'Td' -> Ten of diamonds, '2c' -> 2 of clubs
        """
        if len(s) != 2:
            raise ValueError(f"Card string must be 2 characters, got: '{s}'")
        rank = s[0].upper()
        suit = s[1].lower()
        # Allow lowercase rank input for number cards
        if rank not in RANKS:
            raise ValueError(f"Invalid card string: '{s}'")
        return cls(rank=rank, suit=suit)

    def __str__(self) -> str:
        suit_symbols = {"c": "♣", "d": "♦", "h": "♥", "s": "♠"}
        return f"{self.rank}{suit_symbols[self.suit]}"

    def __repr__(self) -> str:
        return f"Card('{self.rank}{self.suit}')"


# ---------------------------------------------------------------------------
# Hand ranking enum
# ---------------------------------------------------------------------------

class HandRank(IntEnum):
    HIGH_CARD       = 1
    ONE_PAIR        = 2
    TWO_PAIR        = 3
    THREE_OF_A_KIND = 4
    STRAIGHT        = 5
    FLUSH           = 6
    FULL_HOUSE      = 7
    FOUR_OF_A_KIND  = 8
    STRAIGHT_FLUSH  = 9
    ROYAL_FLUSH     = 10


# ---------------------------------------------------------------------------
# Hand result
# ---------------------------------------------------------------------------

@dataclass
class HandResult:
    """Result of evaluating a 5-card hand."""
    rank: HandRank
    rank_name: str
    score: Tuple           # Lexicographically comparable tuple; higher = better
    best_five: List[Card]
    description: str


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _rank_counts(cards: List[Card]) -> Dict[int, int]:
    """Count occurrences of each rank value."""
    counts: Dict[int, int] = {}
    for c in cards:
        counts[c.value] = counts.get(c.value, 0) + 1
    return counts


def _is_flush(cards: List[Card]) -> bool:
    return len({c.suit for c in cards}) == 1


def _straight_high(values: List[int]) -> int:
    """
    Return the high card of the straight, or 0 if not a straight.
    Handles the wheel (A-2-3-4-5) where Ace plays low.
    """
    unique = sorted(set(values), reverse=True)
    if len(unique) < 5:
        return 0
    # Normal straight: top 5 span exactly 4
    if unique[0] - unique[4] == 4:
        return unique[0]
    # Wheel: A-2-3-4-5 (Ace=14, but high card is 5)
    if unique[:5] == [14, 5, 4, 3, 2]:
        return 5
    return 0


def evaluate_five_cards(cards: List[Card]) -> HandResult:
    """
    Evaluate exactly 5 cards and return a HandResult.
    The score tuple allows direct comparison: higher tuple = better hand.
    """
    if len(cards) != 5:
        raise ValueError(f"evaluate_five_cards requires exactly 5 cards, got {len(cards)}")

    values = [c.value for c in cards]
    counts = _rank_counts(cards)
    flush = _is_flush(cards)
    straight_high = _straight_high(values)
    straight = straight_high > 0

    sorted_cards = sorted(cards, key=lambda c: c.value, reverse=True)
    # Sort groups: first by count descending, then by rank value descending
    count_groups = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

    # --- Straight Flush / Royal Flush ---
    if flush and straight:
        if straight_high == 14:
            return HandResult(
                HandRank.ROYAL_FLUSH, "Royal Flush",
                (HandRank.ROYAL_FLUSH, 14),
                sorted_cards, "Royal Flush"
            )
        return HandResult(
            HandRank.STRAIGHT_FLUSH, "Straight Flush",
            (HandRank.STRAIGHT_FLUSH, straight_high),
            sorted_cards, f"Straight Flush, {straight_high} high"
        )

    # --- Four of a Kind ---
    if count_groups[0][1] == 4:
        quad_val = count_groups[0][0]
        kicker = count_groups[1][0]
        return HandResult(
            HandRank.FOUR_OF_A_KIND, "Four of a Kind",
            (HandRank.FOUR_OF_A_KIND, quad_val, kicker),
            sorted_cards, f"Four {RANKS[quad_val - 2]}s"
        )

    # --- Full House ---
    if count_groups[0][1] == 3 and count_groups[1][1] == 2:
        trips_val = count_groups[0][0]
        pair_val = count_groups[1][0]
        return HandResult(
            HandRank.FULL_HOUSE, "Full House",
            (HandRank.FULL_HOUSE, trips_val, pair_val),
            sorted_cards,
            f"Full House, {RANKS[trips_val - 2]}s full of {RANKS[pair_val - 2]}s"
        )

    # --- Flush ---
    if flush:
        kickers = tuple(sorted(values, reverse=True))
        return HandResult(
            HandRank.FLUSH, "Flush",
            (HandRank.FLUSH,) + kickers,
            sorted_cards, f"Flush, {RANKS[kickers[0] - 2]} high"
        )

    # --- Straight ---
    if straight:
        return HandResult(
            HandRank.STRAIGHT, "Straight",
            (HandRank.STRAIGHT, straight_high),
            sorted_cards, f"Straight, {RANKS[straight_high - 2]} high"
        )

    # --- Three of a Kind ---
    if count_groups[0][1] == 3:
        trips_val = count_groups[0][0]
        kickers = tuple(sorted([count_groups[1][0], count_groups[2][0]], reverse=True))
        return HandResult(
            HandRank.THREE_OF_A_KIND, "Three of a Kind",
            (HandRank.THREE_OF_A_KIND, trips_val) + kickers,
            sorted_cards, f"Three {RANKS[trips_val - 2]}s"
        )

    # --- Two Pair ---
    if count_groups[0][1] == 2 and count_groups[1][1] == 2:
        high_pair = max(count_groups[0][0], count_groups[1][0])
        low_pair = min(count_groups[0][0], count_groups[1][0])
        kicker = count_groups[2][0]
        return HandResult(
            HandRank.TWO_PAIR, "Two Pair",
            (HandRank.TWO_PAIR, high_pair, low_pair, kicker),
            sorted_cards,
            f"Two Pair, {RANKS[high_pair - 2]}s and {RANKS[low_pair - 2]}s"
        )

    # --- One Pair ---
    if count_groups[0][1] == 2:
        pair_val = count_groups[0][0]
        kickers = tuple(sorted(
            [count_groups[1][0], count_groups[2][0], count_groups[3][0]], reverse=True
        ))
        return HandResult(
            HandRank.ONE_PAIR, "One Pair",
            (HandRank.ONE_PAIR, pair_val) + kickers,
            sorted_cards, f"Pair of {RANKS[pair_val - 2]}s"
        )

    # --- High Card ---
    kickers = tuple(sorted(values, reverse=True))
    return HandResult(
        HandRank.HIGH_CARD, "High Card",
        (HandRank.HIGH_CARD,) + kickers,
        sorted_cards, f"{RANKS[kickers[0] - 2]} High"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_cards(card_strings: List[str]) -> List[Card]:
    """Parse a list of card strings like ['Ah', 'Kd', 'Tc']."""
    return [Card.from_string(s) for s in card_strings]


def best_hand(hole_cards: List[Card], community_cards: List[Card]) -> HandResult:
    """
    Find the best 5-card hand from hole cards + community cards.

    Requires at least 5 total cards.
    Evaluates all C(n, 5) combinations and returns the strongest.
    """
    all_cards = hole_cards + community_cards
    total = len(all_cards)
    if total < 5:
        raise ValueError(
            f"Need at least 5 cards to evaluate a hand, got {total}. "
            "For preflop analysis, use hand range classification instead."
        )
    if total > 7:
        raise ValueError(f"Maximum 7 cards (2 hole + 5 community), got {total}")

    best: HandResult | None = None
    for combo in combinations(all_cards, 5):
        result = evaluate_five_cards(list(combo))
        if best is None or result.score > best.score:
            best = result

    return best  # type: ignore[return-value]  # guaranteed non-None since total >= 5


def hand_strength_label(result: HandResult) -> str:
    """Return a qualitative strength label for a hand result."""
    rank = result.rank
    if rank >= HandRank.STRAIGHT_FLUSH:
        return "Monster"
    elif rank >= HandRank.FULL_HOUSE:
        return "Very Strong"
    elif rank >= HandRank.STRAIGHT:
        return "Strong"
    elif rank == HandRank.THREE_OF_A_KIND:
        return "Medium-Strong"
    elif rank == HandRank.TWO_PAIR:
        return "Medium"
    elif rank == HandRank.ONE_PAIR:
        return "Weak-Medium"
    else:
        return "Weak"


def compare_hands(hand_a: HandResult, hand_b: HandResult) -> int:
    """
    Compare two hand results.
    Returns:  1 if hand_a wins
             -1 if hand_b wins
              0 if tie
    """
    if hand_a.score > hand_b.score:
        return 1
    elif hand_a.score < hand_b.score:
        return -1
    return 0


# ---------------------------------------------------------------------------
# Preflop hand classification (used when <5 cards are available)
# ---------------------------------------------------------------------------

PREMIUM_HANDS = {("A", "A"), ("K", "K"), ("Q", "Q"), ("A", "K")}
STRONG_HANDS = {("J", "J"), ("T", "T"), ("A", "Q"), ("A", "J"), ("K", "Q")}


def classify_preflop_hand(hole_cards: List[Card]) -> str:
    """
    Classify a preflop hole card combination into a quality tier.
    Used when community cards are not yet available.
    """
    if len(hole_cards) != 2:
        raise ValueError("Preflop classification requires exactly 2 hole cards")

    r1, r2 = hole_cards[0].rank, hole_cards[1].rank
    s1, s2 = hole_cards[0].suit, hole_cards[1].suit
    pair = (r1 == r2)
    suited = (s1 == s2)
    combo = frozenset([r1, r2])

    if {r1, r2} in [{"A", "A"}, {"K", "K"}, {"Q", "Q"}]:
        return "premium"
    if pair:
        v = hole_cards[0].value
        if v >= 9:  # 99+
            return "strong"
        elif v >= 6:  # 66-88
            return "playable"
        else:
            return "speculative"
    if {"A", "K"} == {r1, r2}:
        return "premium"
    if {"A", "Q"} == {r1, r2} or {"A", "J"} == {r1, r2} or {"K", "Q"} == {r1, r2}:
        return "strong"
    if suited and hole_cards[0].value >= 9 and hole_cards[1].value >= 7:
        return "playable"

    return "speculative"


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    hole = parse_cards(["Ah", "Kh"])
    community = parse_cards(["Qh", "Jh", "Th", "2c", "7d"])

    result = best_hand(hole, community)
    print(f"Hand: {result.rank_name}")
    print(f"Description: {result.description}")
    print(f"Strength: {hand_strength_label(result)}")
    print(f"Best five: {[str(c) for c in result.best_five]}")

    preflop_hole = parse_cards(["Ah", "Kd"])
    print(f"\nPreflop AKo classification: {classify_preflop_hand(preflop_hole)}")
