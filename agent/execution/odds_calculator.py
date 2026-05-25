"""
odds_calculator.py
------------------
Deterministic module for calculating approximate poker odds.

Provides:
    - Outs counting (pattern-based, v1)
    - Pot odds calculation
    - Equity estimation (Rule of 2 and 4 + exact formula)
    - Expected value (EV) basics

This module uses no AI reasoning. All calculations are deterministic.
Can be replaced later with a Monte Carlo equity solver or a full solver library.

Public API:
    calculate_pot_odds(pot_size, call_amount)           -> PotOddsResult
    count_outs(hole_cards, community_cards)             -> int
    estimate_equity(outs, cards_to_come, unseen)        -> float
    expected_value(p_win, win_amount, lose_amount)      -> float
    analyze_drawing_odds(hole, community, pot, call, n) -> OddsResult
"""

from dataclasses import dataclass
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PotOddsResult:
    """Result of a pot odds calculation."""
    pot_size: float
    call_amount: float
    total_pot_if_called: float
    pot_odds_ratio: float         # call / (pot + call)
    pot_odds_pct: float           # as percentage
    required_equity_pct: float    # minimum equity to break even


@dataclass
class OddsResult:
    """Combined drawing odds analysis."""
    outs: int
    equity_pct: float             # equity with cards_to_come remaining
    rule_of_2_or_4_pct: float     # quick mental estimate
    pot_odds_result: Optional[PotOddsResult]
    is_profitable_call: Optional[bool]
    call_ev: Optional[float]      # approximate EV of calling (simplified)
    notes: str


# ---------------------------------------------------------------------------
# Pot odds
# ---------------------------------------------------------------------------

def calculate_pot_odds(pot_size: float, call_amount: float) -> PotOddsResult:
    """
    Calculate the pot odds for a call decision.

    Args:
        pot_size:    The pot before the call.
        call_amount: The amount the hero must call.

    Returns:
        PotOddsResult with ratio, percentage, and required equity to break even.
    """
    if call_amount <= 0:
        raise ValueError("call_amount must be positive")
    if pot_size < 0:
        raise ValueError("pot_size cannot be negative")

    total = pot_size + call_amount
    ratio = call_amount / total
    pct = round(ratio * 100, 2)

    return PotOddsResult(
        pot_size=pot_size,
        call_amount=call_amount,
        total_pot_if_called=total,
        pot_odds_ratio=round(ratio, 4),
        pot_odds_pct=pct,
        required_equity_pct=pct,
    )


# ---------------------------------------------------------------------------
# Equity estimation
# ---------------------------------------------------------------------------

def rule_of_two(outs: int) -> float:
    """Approximate equity % with ONE card to come (turn→river or river)."""
    return min(round(outs * 2.0, 1), 100.0)


def rule_of_four(outs: int) -> float:
    """Approximate equity % with TWO cards to come (flop→river)."""
    return min(round(outs * 4.0, 1), 100.0)


def exact_equity_one_card(outs: int, unseen: int = 46) -> float:
    """
    Exact probability of hitting with one card to come.
    Default unseen=46: 52 - 2 hole - 4 community (turn scenario).
    """
    if unseen <= 0:
        return 0.0
    return round((outs / unseen) * 100, 2)


def exact_equity_two_cards(outs: int, unseen: int = 47) -> float:
    """
    Exact probability of hitting at least once with two cards to come.
    Default unseen=47: 52 - 2 hole - 3 community (flop scenario).
    Uses the complement: 1 - P(miss both).
    """
    if unseen <= 0 or outs <= 0:
        return 0.0
    p_miss_turn = (unseen - outs) / unseen
    p_miss_river = (unseen - outs - 1) / (unseen - 1)
    return round((1 - p_miss_turn * p_miss_river) * 100, 2)


def estimate_equity(outs: int, cards_to_come: int, unseen: Optional[int] = None) -> float:
    """
    Estimate equity given outs and cards to come.
    Uses exact formula when unseen is provided, Rule of 2/4 otherwise.
    """
    if unseen is not None:
        if cards_to_come == 1:
            return exact_equity_one_card(outs, unseen)
        else:
            return exact_equity_two_cards(outs, unseen)
    return rule_of_two(outs) if cards_to_come == 1 else rule_of_four(outs)


# ---------------------------------------------------------------------------
# Outs counting (pattern-based, version 1)
# ---------------------------------------------------------------------------

def count_outs(hole_cards_strs: List[str], community_strs: List[str]) -> int:
    """
    Count approximate outs based on detected draw patterns.

    This is a simplified pattern-detection approach for v1.
    It does not enumerate all possible completing cards.
    It does not handle complex scenarios like double-paired boards.

    Args:
        hole_cards_strs:  List of hole card strings, e.g. ["Ah", "Kh"]
        community_strs:   List of community card strings, e.g. ["Qh", "2c", "7h"]

    Returns:
        Approximate number of outs.
    """
    # Inline card parsing to avoid circular imports
    RANKS = "23456789TJQKA"
    RANK_VALUES = {r: i for i, r in enumerate(RANKS, start=2)}

    all_strings = hole_cards_strs + community_strs
    suits = [s[1].lower() for s in all_strings]
    try:
        values = [RANK_VALUES[s[0].upper()] for s in all_strings]
    except KeyError as e:
        raise ValueError(f"Invalid card string: {e}")

    outs = 0
    used_draws: set = set()

    # --- Flush draw: 4 cards of the same suit ---
    for suit in set(suits):
        if suits.count(suit) == 4:
            outs = max(outs, 9)
            used_draws.add("flush")
            break

    # --- Open-Ended Straight Draw (OESD): 4 consecutive ranks ---
    unique_vals = sorted(set(values))
    for i in range(len(unique_vals) - 3):
        window = unique_vals[i: i + 4]
        if window[-1] - window[0] == 3:
            # Verify it's not already part of a 5-card straight
            is_already_straight = any(
                unique_vals[j:j+5][-1] - unique_vals[j:j+5][0] == 4
                for j in range(len(unique_vals) - 4)
                if len(unique_vals[j:j+5]) == 5
            )
            if not is_already_straight and "oesd" not in used_draws:
                outs = max(outs, 8)
                used_draws.add("oesd")

    # --- Gutshot: 4 cards spanning 5 ranks (one gap) ---
    for i in range(len(unique_vals) - 3):
        window = unique_vals[i: i + 4]
        if window[-1] - window[0] == 4 and "gutshot" not in used_draws and "oesd" not in used_draws:
            outs = max(outs, 4)
            used_draws.add("gutshot")

    # --- Combo draw: flush + OESD ---
    if "flush" in used_draws and "oesd" in used_draws:
        # Approximate: not all 15 are clean, use 12 conservatively
        outs = max(outs, 12)

    return outs


# ---------------------------------------------------------------------------
# Expected value
# ---------------------------------------------------------------------------

def expected_value(p_win: float, win_amount: float, lose_amount: float) -> float:
    """
    Calculate the expected value of a decision.

    EV = P(win) * win_amount - P(lose) * lose_amount

    Args:
        p_win:       Probability of winning (0.0 to 1.0)
        win_amount:  Net amount won if you win (the pot you take down)
        lose_amount: Net amount lost if you lose (your call or bet)

    Returns:
        EV in chips. Positive = profitable. Negative = losing play.
    """
    if not (0.0 <= p_win <= 1.0):
        raise ValueError(f"p_win must be between 0 and 1, got {p_win}")
    p_lose = 1.0 - p_win
    return round((p_win * win_amount) - (p_lose * lose_amount), 2)


def is_positive_ev(p_win: float, win_amount: float, lose_amount: float) -> bool:
    return expected_value(p_win, win_amount, lose_amount) > 0


# ---------------------------------------------------------------------------
# Combined analysis
# ---------------------------------------------------------------------------

def analyze_drawing_odds(
    hole_cards: List[str],
    community_cards: List[str],
    pot_size: float = 0.0,
    call_amount: float = 0.0,
    cards_to_come: int = 1,
) -> OddsResult:
    """
    Main analysis function for drawing situations.

    Args:
        hole_cards:     Hole card strings, e.g. ["7h", "8h"]
        community_cards: Community card strings, e.g. ["6h", "9c", "2d"]
        pot_size:       Current pot size before the call
        call_amount:    Amount hero must call (0 = no call needed)
        cards_to_come:  Number of remaining cards (1 = facing river, 2 = facing turn)

    Returns:
        OddsResult with outs, equity, pot odds, and call profitability.
    """
    outs = count_outs(hole_cards, community_cards)

    unseen = 52 - len(hole_cards) - len(community_cards)
    equity = estimate_equity(outs, cards_to_come, unseen)
    approx = rule_of_two(outs) if cards_to_come == 1 else rule_of_four(outs)

    pot_odds_result: Optional[PotOddsResult] = None
    is_profitable: Optional[bool] = None
    call_ev: Optional[float] = None

    if pot_size > 0 and call_amount > 0:
        pot_odds_result = calculate_pot_odds(pot_size, call_amount)
        is_profitable = equity >= pot_odds_result.required_equity_pct
        # Simplified EV of calling: win the pot if draw hits, lose call amount otherwise
        p_win = equity / 100.0
        call_ev = expected_value(p_win, pot_size, call_amount)

    # Build notes
    parts = []
    if outs == 0:
        parts.append("No clear drawing outs detected. This is likely a made hand or air.")
    else:
        parts.append(f"{outs} outs detected.")
        rule_label = "Rule of 2" if cards_to_come == 1 else "Rule of 4"
        parts.append(f"{rule_label}: ~{approx:.0f}% equity. Exact: {equity:.1f}%.")
    if pot_odds_result:
        parts.append(
            f"Pot odds: {pot_odds_result.pot_odds_pct:.1f}% required equity. "
            f"Call is {'profitable ✓' if is_profitable else 'unprofitable ✗'}."
        )
    if call_ev is not None:
        parts.append(f"Approximate call EV: {call_ev:+.1f} chips.")

    return OddsResult(
        outs=outs,
        equity_pct=equity,
        rule_of_2_or_4_pct=approx,
        pot_odds_result=pot_odds_result,
        is_profitable_call=is_profitable,
        call_ev=call_ev,
        notes=" | ".join(parts),
    )


# ---------------------------------------------------------------------------
# Common draw reference table
# ---------------------------------------------------------------------------

DRAW_REFERENCE = {
    "flush_draw":              {"outs": 9,  "description": "4 to a flush"},
    "open_ended_straight":     {"outs": 8,  "description": "4 consecutive cards (OESD)"},
    "two_overcards":           {"outs": 6,  "description": "2 overcards to the board"},
    "gutshot_straight":        {"outs": 4,  "description": "Inside straight draw"},
    "one_overcard":            {"outs": 3,  "description": "1 overcard to the board"},
    "pair_to_trips":           {"outs": 2,  "description": "One pair, need trips"},
    "flush_plus_oesd":         {"outs": 15, "description": "Flush draw + OESD (approx)"},
    "flush_plus_gutshot":      {"outs": 12, "description": "Flush draw + gutshot (approx)"},
    "set_to_full_house_quads": {"outs": 7,  "description": "Set improving to full house or quads"},
}


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Flush draw + OESD on the flop
    hole = ["7h", "8h"]
    community = ["6h", "9c", "2h"]

    result = analyze_drawing_odds(
        hole_cards=hole,
        community_cards=community,
        pot_size=100,
        call_amount=40,
        cards_to_come=2,
    )

    print("=== Drawing Odds Analysis ===")
    print(f"Outs:              {result.outs}")
    print(f"Equity (exact):    {result.equity_pct}%")
    print(f"Rule of 4 approx:  {result.rule_of_2_or_4_pct}%")
    print(f"Profitable call:   {result.is_profitable_call}")
    print(f"Call EV:           {result.call_ev}")
    print(f"Notes: {result.notes}")

    # Pot odds example
    po = calculate_pot_odds(pot_size=200, call_amount=80)
    print(f"\n=== Pot Odds ===")
    print(f"Required equity: {po.required_equity_pct}%")

    # EV example
    ev = expected_value(p_win=0.36, win_amount=200, lose_amount=40)
    print(f"\n=== EV of calling with flush draw ===")
    print(f"EV: {ev:+.2f} chips")
