"""
agent_bridge.py
---------------
The bridge between the application layer and the agent system.

This service:
1. Receives structured inputs from the API routers
2. Calls the deterministic execution scripts for mechanical calculations
3. Produces coaching analysis using rule-based logic (v1)
4. Logs decisions to the session store

VERSION 1 ARCHITECTURE:
The coaching analysis is rule-based (heuristic). It produces realistic,
educational feedback without requiring a live LLM connection.

TO CONNECT AN LLM (future):
Replace _rule_based_analysis() with a call to your LLM provider.
The input prompt is pre-formatted and model-agnostic.
The output schema (DecisionAnalysis) stays the same.

This class is the ONLY point in the application that knows about
the agent system. The routers never import from /agent directly.
"""

import sys
import uuid
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.parent.parent
AGENT_EXEC = REPO_ROOT / "agent" / "execution"
APP_SHARED = REPO_ROOT / "app" / "shared"

for p in [str(REPO_ROOT), str(AGENT_EXEC), str(APP_SHARED)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from hand_evaluator import (
    parse_cards,
    best_hand,
    hand_strength_label,
    classify_preflop_hand,
    HandRank,
)
from odds_calculator import (
    calculate_pot_odds,
    count_outs,
    estimate_equity,
    analyze_drawing_odds,
)
from decision_logger import DecisionLogger, create_decision_record

from schemas import (
    DecisionAnalysis,
    HandReview,
    KeyDecision,
    StreetGrade,
    SessionSummaryRequest,
    SessionSummaryResponse,
    SessionReport,
    RatingEnum,
    ActionEnum,
    StreetEnum,
    OutcomeClassificationEnum,
)


# ---------------------------------------------------------------------------
# Action legality validation
# ---------------------------------------------------------------------------

def validate_action_legality(
    user_action: str,
    available_actions: List[str],
    bet_amount: Optional[float],
) -> None:
    """
    Raise ValueError if the user's action is not legal in this scenario.
    This enforces the contract: only actions listed in available_actions are valid.
    """
    if user_action not in available_actions:
        raise ValueError(
            f"Action '{user_action}' is not available. "
            f"Legal actions are: {', '.join(available_actions)}"
        )
    if user_action in ("bet", "raise") and (bet_amount is None or bet_amount <= 0):
        raise ValueError(f"A positive bet_amount is required for action '{user_action}'")


# ---------------------------------------------------------------------------
# Analysis heuristics
# ---------------------------------------------------------------------------

def _evaluate_hand_context(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate the hero's hand strength and drawing potential.
    Returns a context dict used by the analysis logic.
    """
    hole = scenario.get("hole_cards", [])
    community = scenario.get("community_cards", [])
    street = scenario.get("street", "preflop")

    result = {
        "hand_result": None,
        "hand_strength_label": "Unknown",
        "hand_rank": None,
        "outs": 0,
        "equity_pct": 0.0,
        "preflop_class": None,
    }

    # Preflop: classify hand range
    if street == "preflop" or len(community) == 0:
        try:
            hole_cards = parse_cards(hole)
            result["preflop_class"] = classify_preflop_hand(hole_cards)
        except Exception:
            result["preflop_class"] = "unknown"
        return result

    # Postflop: evaluate hand strength
    if len(hole) + len(community) >= 5:
        try:
            hole_cards = parse_cards(hole)
            community_cards = parse_cards(community)
            hand_result = best_hand(hole_cards, community_cards)
            result["hand_result"] = hand_result
            result["hand_strength_label"] = hand_strength_label(hand_result)
            result["hand_rank"] = hand_result.rank
        except Exception:
            pass

    # Count outs for draws
    try:
        result["outs"] = count_outs(hole, community)
        cards_to_come = 2 if street == "flop" else 1
        unseen = 52 - len(hole) - len(community)
        result["equity_pct"] = estimate_equity(result["outs"], cards_to_come, unseen)
    except Exception:
        pass

    return result


def _is_in_position(hero_position: str) -> bool:
    """Approximate check: BTN, CO, HJ are typically in position."""
    return hero_position.upper() in ("BTN", "CO", "HJ")


def _rule_based_analysis(
    scenario: Dict[str, Any],
    user_action: str,
    bet_amount: Optional[float],
    user_level: str,
    hand_ctx: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Rule-based coaching analysis for version 1.

    In production, this function would build a structured prompt and
    send it to an LLM (Claude, GPT-4, local model, etc.).
    The output schema (DecisionAnalysis fields) remains the same.

    Current logic:
    - Uses hand strength, position, and action type heuristics
    - Produces realistic educational feedback
    - Adapts key concepts to the decision type
    """
    street = scenario.get("street", "flop")
    pot_size = float(scenario.get("pot_size", 100))
    hero_position = scenario.get("hero_position", "BTN")
    ip = _is_in_position(hero_position)

    hand_rank = hand_ctx.get("hand_rank")
    hand_label = hand_ctx.get("hand_strength_label", "Unknown")
    outs = hand_ctx.get("outs", 0)
    equity = hand_ctx.get("equity_pct", 0.0)
    preflop_class = hand_ctx.get("preflop_class")

    # Default values
    rating = RatingEnum.OK
    score = 6
    explanation = ""
    best_alternative = ""
    recommended_sizing = None
    risk_analysis = ""
    luck_vs_strategy = "Strategy. This decision is within your control."
    key_concept = ""
    recommended_drill = "Continue practicing decision-making in similar spots."

    # ----- PREFLOP -----
    if street == "preflop":
        if preflop_class == "premium":
            # Detect if we are facing a villain raise (not just a hero open)
            facing_villain_raise = any(
                a.get("action") in ("raise", "bet")
                for a in scenario.get("action_history", [])
                if not a.get("player", "").lower().startswith("hero")
            )
            if user_action == "raise":
                rating, score = RatingEnum.GOOD, 10
                explanation = (
                    "3-betting with a premium hand in position is the correct aggressive play. "
                    "Premium hands (AA, KK, QQ, AKs) should almost always be 3-bet against an open. "
                    "You build a large pot with the best of it, narrow the field, and leverage your position."
                )
                best_alternative = "This is the recommended play."
                risk_analysis = "Minimal. You may face a 4-bet, but even then premium hands have strong equity."
                key_concept = "preflop aggression"
                recommended_drill = "Practice 3-betting premium hands from all positions — BTN, CO, HJ."
            elif user_action == "call":
                if facing_villain_raise:
                    rating, score = RatingEnum.OK, 7
                    explanation = (
                        "Calling with a premium hand is not a blunder, but it is too passive. "
                        "Against a CO open on the button, A-K suited and big pairs should 3-bet — "
                        "not flat call. Calling lets speculative hands enter cheaply, surrenders initiative, "
                        "and fails to build the pot when you have the best of it."
                    )
                    best_alternative = "3-bet to build the pot, narrow the field, and define villain's range."
                    risk_analysis = (
                        "Flat calling invites multi-way pots where your equity advantage shrinks. "
                        "You also give up the chance to win the pot immediately vs weaker holdings."
                    )
                    key_concept = "preflop aggression"
                    recommended_drill = "Practice 3-betting premium hands in position. Flat-calling AK is a common leak."
                else:
                    rating, score = RatingEnum.OK, 7
                    explanation = (
                        "Limping or calling with a premium hand surrenders initiative. "
                        "Open-raise to build the pot and define your range."
                    )
                    best_alternative = "Open-raise (3–4x BB) with premium hands."
                    risk_analysis = "Limping invites multi-way pots and reduces your equity advantage."
                    key_concept = "preflop aggression"
                    recommended_drill = "Practice open-raising with premium hands from every position."
            elif user_action == "fold":
                rating, score = RatingEnum.BLUNDER, 1
                explanation = "You folded a premium hand preflop. This is a significant mistake."
                best_alternative = "Raise (3-bet) — premium hands should always play."
                risk_analysis = "No risk justifies folding a premium hand preflop."
                key_concept = "preflop hand selection"
                recommended_drill = "Study basic preflop hand ranges. Premium hands always play."

        elif preflop_class in ("strong", "playable"):
            if user_action == "call":
                rating, score = RatingEnum.OK, 6
                explanation = (
                    "Calling with a strong hand is acceptable, though raising would often be better "
                    "to build the pot and create more favorable post-flop situations."
                )
                best_alternative = "Consider raising (3-betting) to build the pot and gain initiative."
                risk_analysis = "Calling is passive — you give up pot equity and initiative."
                key_concept = "preflop aggression vs passive play"
                recommended_drill = "Practice 3-betting strong hands in position."
            elif user_action == "raise":
                rating, score = RatingEnum.GOOD, 8
                explanation = "Raising with a strong hand builds the pot and narrows the field. Correct."
                best_alternative = "This is the recommended play."
                risk_analysis = "Standard risk — you may face a 4-bet from very strong hands."
                key_concept = "preflop aggression"
                recommended_drill = "Refine your 3-bet sizing for different positions."
            elif user_action == "fold":
                rating, score = RatingEnum.MISTAKE, 3
                explanation = "Folding a strong hand preflop is usually wrong — you have too much value."
                best_alternative = "Call at minimum. Consider raising."
                risk_analysis = "Folding surrenders equity you hold by default."
                key_concept = "preflop hand selection"
                recommended_drill = "Review preflop opening ranges for your position."

        else:  # speculative or trash
            if user_action == "fold":
                rating, score = RatingEnum.GOOD, 8
                explanation = (
                    "Folding a speculative or weak hand preflop, especially facing aggression, "
                    "is usually correct. You preserve your stack for better spots."
                )
                best_alternative = "This is the correct play in most cases."
                risk_analysis = "No significant risk — speculative hands need good implied odds to continue."
                key_concept = "preflop discipline"
                recommended_drill = "Study preflop ranges: which hands are worth playing from each position?"
            else:
                rating, score = RatingEnum.MISTAKE, 4
                explanation = (
                    "Continuing with a speculative hand without favorable odds or position "
                    "will lose money over time."
                )
                best_alternative = "Fold and wait for a better spot."
                risk_analysis = "Weak hands have poor equity and often miss the board entirely."
                key_concept = "preflop discipline"
                recommended_drill = "Practice folding weak hands preflop. Patience is a skill."

    # ----- FLOP -----
    elif street == "flop":
        if hand_rank is not None and hand_rank >= HandRank.TWO_PAIR:
            # Very strong hand
            if user_action == "check":
                rating, score = RatingEnum.MISTAKE, 3
                explanation = (
                    f"You have a {hand_label.lower()} — a very strong holding on the flop. "
                    "Checking gives your opponent a free card and loses significant value. "
                    "This board needs a bet for value."
                )
                best_alternative = "Bet for value (50–75% pot)"
                recommended_sizing = f"50–75% pot ({round(pot_size * 0.5):.0f}–{round(pot_size * 0.75):.0f} chips)"
                risk_analysis = "Free cards can improve the opponent's hand. Builds less of the pot when ahead."
                key_concept = "value betting strong hands"
                recommended_drill = "Practice betting two pair and better on all board textures."
            elif user_action in ("bet", "raise"):
                rating, score = RatingEnum.GOOD, 9
                explanation = f"Betting with {hand_label.lower()} is the correct play. You build the pot while ahead."
                best_alternative = "This is correct."
                risk_analysis = "Minimal — you have a strong hand. Risk is losing to a bigger hand (unlikely)."
                key_concept = "value betting"
                recommended_drill = "Practice bet sizing for very strong hands on different board textures."

        elif hand_rank == HandRank.ONE_PAIR:
            # Top pair or better pair
            if user_action == "check":
                if ip:
                    rating, score = RatingEnum.MISTAKE, 4
                    explanation = (
                        "You have one pair in position, and the opponent checked to you. "
                        "Checking back misses value — you should bet when ahead and in position."
                    )
                    best_alternative = "Bet for value (33–66% pot)"
                    recommended_sizing = f"33–66% pot ({round(pot_size * 0.33):.0f}–{round(pot_size * 0.66):.0f} chips)"
                    risk_analysis = "Checking gives a free card and loses value from worse hands."
                    key_concept = "value betting in position"
                    recommended_drill = "Practice c-betting top pair in position on dry boards."
                else:
                    rating, score = RatingEnum.OK, 6
                    explanation = "Check-calling or check-raising with one pair out of position is a valid line."
                    best_alternative = "Leading out with a bet is also fine — both lines have merit."
                    risk_analysis = "Checking OOP can be exploited if you check too often."
                    key_concept = "out-of-position play with one pair"
                    recommended_drill = "Practice check-raising vs donk-betting from the BB."
            elif user_action in ("bet", "raise"):
                rating, score = RatingEnum.GOOD, 8
                explanation = "Betting one pair for value is the correct approach here."
                best_alternative = "This is correct."
                risk_analysis = "Standard risk — opponent could have a better hand."
                key_concept = "value betting"
                recommended_drill = "Refine your bet sizing with one pair (33–66% pot usually optimal)."

        elif outs >= 8:
            # Strong draw (flush draw, OESD, combo)
            if user_action == "check":
                rating, score = RatingEnum.OK, 5
                explanation = (
                    f"You have a strong draw ({outs} outs, ~{equity:.0f}% equity). "
                    "Checking is passable, but semi-bluffing by betting often has better EV — "
                    "you can win immediately by fold equity OR by hitting your draw."
                )
                best_alternative = f"Consider a semi-bluff bet (50–75% pot) to add fold equity"
                risk_analysis = "Semi-bluffing risks chips but gains fold equity. Passive play leaves EV behind."
                key_concept = "semi-bluffing with strong draws"
                recommended_drill = "Practice semi-bluffing on the flop with 8+ outs."
            elif user_action in ("bet", "raise"):
                rating, score = RatingEnum.GOOD, 8
                explanation = (
                    f"Semi-bluffing with {outs} outs is the correct aggressive play. "
                    "You can win by making the opponent fold OR by improving to the best hand."
                )
                best_alternative = "This is correct."
                risk_analysis = "You may be called and need to hit your draw."
                key_concept = "semi-bluffing"
                recommended_drill = "Practice semi-bluff sizing to balance your range."

        else:
            # Weak hand, no significant draw
            if user_action == "check":
                rating, score = RatingEnum.GOOD, 8
                explanation = (
                    "With a weak hand and no significant draw, checking is the right play. "
                    "Don't bluff without a reason — preserve your chips."
                )
                best_alternative = "This is correct."
                risk_analysis = "No risk — you're not investing chips with a weak holding."
                key_concept = "pot control with weak hands"
                recommended_drill = "Practice identifying when to give up vs continue bluffing."
            elif user_action in ("bet", "raise"):
                rating, score = RatingEnum.MISTAKE, 3
                explanation = (
                    "Betting with a weak hand and no real draw is a poor bluff. "
                    "Without fold equity or the ability to improve, this loses chips over time."
                )
                best_alternative = "Check (give up this street)"
                risk_analysis = "Betting without equity means you lose when called, which is often."
                key_concept = "bluff selection"
                recommended_drill = "Study when bluffing is profitable — you need fold equity."

    # ----- TURN -----
    elif street == "turn":
        if hand_rank is not None and hand_rank >= HandRank.ONE_PAIR:
            if user_action == "check":
                if ip and hand_rank >= HandRank.TWO_PAIR:
                    rating, score = RatingEnum.MISTAKE, 3
                    explanation = (
                        f"You have {hand_label.lower()} on the turn and checked. "
                        "Strong hands should bet on the turn to build the pot and deny free cards to draws."
                    )
                    best_alternative = "Bet for value (50–75% pot)"
                    recommended_sizing = f"{round(pot_size * 0.5):.0f}–{round(pot_size * 0.75):.0f} chips"
                    risk_analysis = "Free cards on the river can complete draws and cost you the pot."
                    key_concept = "protection and value on the turn"
                    recommended_drill = "Practice betting the turn with strong made hands."
                else:
                    rating, score = RatingEnum.OK, 6
                    explanation = "Checking the turn with one pair can be correct — controls pot size."
                    best_alternative = "Betting for value is also valid."
                    risk_analysis = "Checking gives up value but controls the pot."
                    key_concept = "pot control"
                    recommended_drill = "Study when to bet vs check the turn with one pair."
            elif user_action in ("bet", "raise"):
                rating, score = RatingEnum.GOOD, 8
                explanation = "Betting your made hand on the turn for value is correct."
                best_alternative = "This is correct."
                risk_analysis = "Standard risk — opponent could have improved."
                key_concept = "turn value betting"
                recommended_drill = "Practice turn bet sizing: usually 50–75% pot with strong hands."

    # ----- RIVER -----
    elif street == "river":
        action_history = scenario.get("action_history", [])
        villain_bet = next(
            (a.get("amount") for a in action_history if a.get("action") == "bet"),
            None,
        )

        if villain_bet and user_action == "call":
            # Evaluate pot odds
            try:
                pot_odds_result = calculate_pot_odds(pot_size, float(villain_bet))
                required_equity = pot_odds_result.required_equity_pct

                if hand_rank and hand_rank >= HandRank.TWO_PAIR:
                    rating, score = RatingEnum.GOOD, 8
                    explanation = (
                        f"Calling with {hand_label.lower()} against a river bet is correct. "
                        "You beat most of the villain's value range."
                    )
                    best_alternative = "This is correct. Consider raising for thin value."
                    risk_analysis = "Risk is facing the top of villain's range."
                    key_concept = "river calling with strong hands"
                    recommended_drill = "Practice identifying when to call vs raise the river."
                elif hand_rank == HandRank.ONE_PAIR:
                    rating, score = RatingEnum.OK, 6
                    explanation = (
                        f"Calling with one pair on the river requires {required_equity:.1f}% equity to break even. "
                        "One pair can be correct to call depending on villain's bet sizing and tendencies."
                    )
                    best_alternative = f"Pot odds require ~{required_equity:.1f}% equity. Evaluate if one pair beats enough of villain's range."
                    risk_analysis = "One pair is a bluff-catch — you need villain to be bluffing often enough."
                    key_concept = "river bluff catching"
                    recommended_drill = "Practice pot odds calculation on river calls."
                else:
                    rating, score = RatingEnum.MISTAKE, 4
                    explanation = (
                        "Calling a river bet with a weak hand is often a mistake. "
                        f"You needed {required_equity:.1f}% equity to break even, but your hand has limited showdown value."
                    )
                    best_alternative = "Fold — save your chips for spots where you have better equity."
                    risk_analysis = "Calling here loses when villain has any made hand."
                    key_concept = "river pot odds and fold discipline"
                    recommended_drill = "Practice folding weak hands to river bets. Calculate equity before calling."

            except Exception:
                pass

        elif user_action == "fold":
            rating, score = RatingEnum.OK, 6
            explanation = "Folding to a river bet can be correct, especially with a weak hand."
            best_alternative = "Evaluate pot odds before folding if you have any showdown value."
            risk_analysis = "Over-folding on the river is exploitable."
            key_concept = "river fold discipline"
            recommended_drill = "Practice identifying when to fold vs call on the river."

    # Luck vs strategy — score-based framing
    if score >= 9:
        luck_vs_strategy = (
            "Strategy. You made the best play based on the available information."
        )
    elif score >= 7:
        luck_vs_strategy = (
            "Strategy. Your play is reasonable, but there is a more profitable option."
        )
    elif score >= 5:
        luck_vs_strategy = (
            "Review. This decision misses an important poker concept."
        )
    else:
        luck_vs_strategy = (
            "Discipline check. This is a spot to slow down and review the fundamentals."
        )

    # Derive a short best_action_label from best_alternative for display near the score
    import re as _re
    _action_pat = _re.compile(
        r'^(Fold|Call|Raise|3-bet|Open-raise|Bet|Check|Semi-bluff)', _re.IGNORECASE
    )
    _m = _action_pat.match(best_alternative) if best_alternative else None
    best_action_label = _m.group(1) if _m else ""

    # Derive mistake_category from key_concept + rating
    mistake_category: Optional[str] = None
    if rating in (RatingEnum.MISTAKE, RatingEnum.BLUNDER):
        concept_to_category: Dict[str, str] = {
            "value betting": "missed_value",
            "value betting strong hands": "missed_value",
            "value betting in position": "passive_play",
            "semi-bluffing with strong draws": "passive_play",
            "preflop aggression": "passive_play",
            "preflop hand selection": "hand_selection",
            "preflop discipline": "hand_selection",
            "bluff selection": "over_bluff",
            "river pot odds and fold discipline": "calling_station",
            "protection and value on the turn": "passive_play",
        }
        mistake_category = concept_to_category.get(key_concept, "general_mistake")

    return {
        "rating": rating,
        "score": score,
        "explanation": explanation,
        "best_alternative": best_alternative,
        "best_action_label": best_action_label,
        "recommended_sizing": recommended_sizing,
        "risk_analysis": risk_analysis,
        "luck_vs_strategy": luck_vs_strategy,
        "key_concept": key_concept,
        "mistake_category": mistake_category,
        "recommended_drill": recommended_drill,
    }


# ---------------------------------------------------------------------------
# Agent Bridge
# ---------------------------------------------------------------------------

class AgentBridge:
    """
    Bridge between the application and the agent system.

    Version 1: Uses rule-based heuristics + deterministic execution scripts.
    Future: Replace _rule_based_analysis() with an LLM call.
    """

    async def analyze_decision(
        self,
        session_id: str,
        scenario: Dict[str, Any],
        user_action: str,
        bet_amount: Optional[float],
        user_level: str,
        log_decision: bool = True,
    ) -> DecisionAnalysis:
        """
        Analyze a user's poker decision and return coaching feedback.
        """
        # 0. Validate action legality
        available = [a.value if hasattr(a, "value") else str(a) for a in scenario.get("available_actions", [])]
        try:
            validate_action_legality(user_action, available, bet_amount)
        except ValueError as exc:
            # Return a blunder rating rather than a 422 so the UI can still show feedback
            from schemas import RatingEnum
            return DecisionAnalysis(
                scenario_id=scenario.get("scenario_id", "unknown"),
                user_action=ActionEnum(user_action) if user_action in [a.value for a in ActionEnum] else ActionEnum.FOLD,
                bet_amount=bet_amount,
                rating=RatingEnum.BLUNDER,
                rating_score=1,
                explanation=str(exc),
                best_alternative=f"Choose one of: {', '.join(available)}",
                risk_analysis="Illegal action submitted.",
                luck_vs_strategy="Strategy. The action you chose is not available in this scenario.",
                recommended_drill="Review the available actions before deciding.",
            )

        # 1. Evaluate hand context (deterministic)
        hand_ctx = _evaluate_hand_context(scenario)

        # 2. Run analysis (rule-based in v1, LLM in production)
        analysis_raw = _rule_based_analysis(
            scenario=scenario,
            user_action=user_action,
            bet_amount=bet_amount,
            user_level=user_level,
            hand_ctx=hand_ctx,
        )

        decision_id = str(uuid.uuid4())

        # 3. Log the decision
        if log_decision:
            try:
                logger = DecisionLogger(session_id=session_id)
                record = create_decision_record(
                    session_id=session_id,
                    scenario=scenario,
                    user_action=user_action,
                    bet_amount=bet_amount,
                    rating=analysis_raw["rating"].value,
                    rating_score=analysis_raw["score"],
                    user_level=user_level,
                    analysis_id=decision_id,
                    mistake_category=analysis_raw.get("mistake_category"),
                    explanation_summary=analysis_raw["explanation"][:200],
                    recommended_action=analysis_raw["best_alternative"][:120],
                )
                logger.log(record)
            except Exception:
                pass  # Logging failure should not block the response

        # 4. Build hand strength description
        hand_result = hand_ctx.get("hand_result")
        hand_strength = None
        if hand_result:
            hand_strength = f"{hand_result.rank_name} ({hand_result.description})"
        elif hand_ctx.get("preflop_class"):
            hand_strength = f"Preflop class: {hand_ctx['preflop_class']}"

        position_note = None
        hero_pos = scenario.get("hero_position", "")
        if hero_pos:
            ip = _is_in_position(hero_pos)
            position_note = (
                f"Hero is in position ({hero_pos}). Acting last gives information advantage."
                if ip else
                f"Hero is out of position ({hero_pos}). Acting first requires more caution."
            )

        return DecisionAnalysis(
            decision_id=decision_id,
            scenario_id=scenario.get("scenario_id", "unknown"),
            user_action=ActionEnum(user_action),
            bet_amount=bet_amount,
            rating=analysis_raw["rating"],
            rating_score=analysis_raw["score"],
            hand_strength=hand_strength,
            position_note=position_note,
            explanation=analysis_raw["explanation"],
            best_alternative=analysis_raw["best_alternative"],
            best_action_label=analysis_raw.get("best_action_label", ""),
            recommended_sizing=analysis_raw.get("recommended_sizing"),
            risk_analysis=analysis_raw["risk_analysis"],
            luck_vs_strategy=analysis_raw["luck_vs_strategy"],
            key_concept=analysis_raw.get("key_concept"),
            mistake_category=analysis_raw.get("mistake_category"),
            recommended_drill=analysis_raw["recommended_drill"],
            learning_objective=scenario.get("learning_objective"),
        )

    async def review_hand(
        self,
        session_id: str,
        hand_id: str,
        decisions: list,
        showdown_result: Optional[Dict[str, Any]] = None,
    ) -> HandReview:
        """
        Generate a full hand review from a sequence of decisions.
        Version 1: Aggregates individual decision analyses.
        """
        if not decisions:
            raise ValueError("No decisions provided for hand review")

        # Analyze each decision
        street_analyses: Dict[str, Dict[str, Any]] = {}
        worst_decision = None
        worst_score = 11

        for req in decisions:
            scenario = req.scenario_data
            if scenario is None:
                continue

            scenario_dict = scenario.model_dump() if hasattr(scenario, "model_dump") else dict(scenario)
            hand_ctx = _evaluate_hand_context(scenario_dict)
            analysis = _rule_based_analysis(
                scenario=scenario_dict,
                user_action=req.user_action.value,
                bet_amount=req.bet_amount,
                user_level=req.user_level.value,
                hand_ctx=hand_ctx,
            )

            street = scenario_dict.get("street", "unknown")
            street_analyses[street] = {
                "rating": analysis["rating"],
                "score": analysis["score"],
                "note": analysis["explanation"][:120] + "..." if len(analysis["explanation"]) > 120 else analysis["explanation"],
                "user_action": req.user_action.value,
                "optimal_action": analysis["best_alternative"],
                "scenario": scenario_dict,
                "analysis": analysis,
            }

            if analysis["score"] < worst_score:
                worst_score = analysis["score"]
                worst_decision = (street, analysis)

        # Build street grades
        street_grades: Dict[str, StreetGrade] = {}
        for street, data in street_analyses.items():
            street_grades[street] = StreetGrade(
                rating=data["rating"],
                score=data["score"],
                note=data["note"],
            )

        # Key decision = worst decision
        if worst_decision:
            key_street, key_analysis = worst_decision
            key_decision = KeyDecision(
                street=StreetEnum(key_street) if key_street in StreetEnum._value2member_map_ else StreetEnum.FLOP,
                hero_action=street_analyses.get(key_street, {}).get("user_action", "unknown"),
                optimal_action=key_analysis["best_alternative"],
                sizing_recommendation=key_analysis.get("recommended_sizing"),
                explanation=key_analysis["explanation"],
            )
        else:
            key_decision = KeyDecision(
                street=StreetEnum.FLOP,
                hero_action="unknown",
                optimal_action="unknown",
                explanation="No key decision identified.",
            )

        # Overall grade
        scores = [d["score"] for d in street_analyses.values()]
        avg_score = sum(scores) / len(scores) if scores else 5
        if avg_score >= 8:
            overall_grade = RatingEnum.GOOD
        elif avg_score >= 5:
            overall_grade = RatingEnum.OK
        elif avg_score >= 2:
            overall_grade = RatingEnum.MISTAKE
        else:
            overall_grade = RatingEnum.BLUNDER

        # Outcome classification
        outcome = "unknown"
        if showdown_result:
            outcome = showdown_result.get("winner", "unknown")
            if outcome == "hero":
                outcome = "win"
            elif outcome == "villain":
                outcome = "loss"

        mistake_count = sum(1 for d in street_analyses.values() if d["rating"] in (RatingEnum.MISTAKE, RatingEnum.BLUNDER))
        if mistake_count == 0:
            outcome_class = OutcomeClassificationEnum.LUCK_LOSS if outcome == "loss" else OutcomeClassificationEnum.STRATEGY_WIN
        elif mistake_count == len(street_analyses):
            outcome_class = OutcomeClassificationEnum.STRATEGY_LOSS
        else:
            outcome_class = OutcomeClassificationEnum.MIXED

        # Primary lesson
        primary_lesson = "Continue practicing the fundamentals."
        if worst_decision:
            _, key_analysis = worst_decision
            primary_lesson = key_analysis.get("recommended_drill", primary_lesson)

        return HandReview(
            hand_id=hand_id,
            session_id=session_id,
            outcome=outcome,
            outcome_classification=outcome_class,
            key_decision=key_decision,
            street_grades=street_grades,
            luck_vs_strategy=worst_decision[1]["luck_vs_strategy"] if worst_decision else "Correct play throughout.",
            primary_lesson=primary_lesson,
            recommended_drill=primary_lesson,
            overall_grade=overall_grade,
            overall_score=round(avg_score),
        )

    async def save_session(self, request: SessionSummaryRequest) -> SessionSummaryResponse:
        """Save a session summary to the memory files."""
        # In v1, the decision logger already saved individual decisions.
        # Here we just confirm.
        return SessionSummaryResponse(
            session_id=request.session_id,
            saved=True,
            message=f"Session {request.session_id} saved. {request.total_decisions} decisions logged.",
        )

    async def get_session_summary(self, session_id: str) -> Optional[SessionReport]:
        """Retrieve a rich session report from the decision log."""
        try:
            logger = DecisionLogger(session_id=session_id)
            records = logger.read_session()
            if not records:
                return None

            scores = [r.rating_score for r in records]
            ratings = [r.rating for r in records]
            total = len(records)
            avg_score = round(sum(scores) / total, 2)
            good_ok = sum(1 for r in ratings if r in ("good", "ok"))
            accuracy_pct = round(good_ok / total * 100, 1)

            streets: Dict[str, int] = {}
            for r in records:
                streets[r.street] = streets.get(r.street, 0) + 1

            strongest = max(records, key=lambda r: r.rating_score)
            weakest   = min(records, key=lambda r: r.rating_score)

            # Recurring mistake — most common mistake category among mistakes/blunders
            mistake_cats: Dict[str, int] = {}
            for r in records:
                if r.rating in ("mistake", "blunder") and getattr(r, "mistake_category", None):
                    mc = r.mistake_category
                    mistake_cats[mc] = mistake_cats.get(mc, 0) + 1
            recurring_mistake = max(mistake_cats, key=mistake_cats.get) if mistake_cats else None

            # Recommended drill from most common weak spot
            drill_map: Dict[str, str] = {
                "passive_play":    "Practice betting for value — identify spots where you should bet but checked.",
                "missed_value":    "Practice value betting thin on the river and turn.",
                "hand_selection":  "Review preflop hand ranges and practice folding weak hands.",
                "over_bluff":      "Practice bluff selection — only bluff with fold equity or draws.",
                "calling_station": "Practice folding to river bets — calculate pot odds before calling.",
                "sizing_error":    "Drill bet sizing: 33% (block), 50% (standard), 75% (value/protection).",
                "general_mistake": "Review the fundamentals: position, hand strength, pot odds.",
            }
            recommended_drill = drill_map.get(recurring_mistake or "", "Keep practicing — no major pattern detected.") if recurring_mistake else "Strong session. Keep refining your fundamentals."

            # Progress note
            if avg_score >= 8:
                note = "Excellent session — most decisions were correct."
            elif avg_score >= 6:
                note = "Good session. Focus on the identified weaknesses."
            elif avg_score >= 4:
                note = "Developing session. Work on the drills below."
            else:
                note = "Challenging session — review the fundamentals before continuing."

            return SessionReport(
                session_id=session_id,
                total_decisions=total,
                average_score=avg_score,
                accuracy_pct=accuracy_pct,
                strongest_decision={
                    "street": strongest.street,
                    "action": strongest.user_action,
                    "score": strongest.rating_score,
                    "rating": strongest.rating,
                },
                weakest_decision={
                    "street": weakest.street,
                    "action": weakest.user_action,
                    "score": weakest.rating_score,
                    "rating": weakest.rating,
                    "category": getattr(weakest, "mistake_category", None),
                },
                recurring_mistake=recurring_mistake,
                recommended_drill=recommended_drill,
                progress_note=note,
                streets_played=streets,
            )
        except Exception:
            return None
