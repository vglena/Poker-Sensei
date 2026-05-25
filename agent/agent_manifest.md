# Agent Manifest — Poker Training System

## Purpose

This agent system is the cognitive backbone of the Poker Training Application.
It provides coaching, strategy analysis, hand review, scenario generation, and adaptive feedback.

It is **model-agnostic**: it does not depend on any specific AI provider.
The application layer (`/app`) connects to this system through a defined bridge interface.

This is an educational system only. It does not support real-money gambling.

---

## Responsibilities

- Analyze player decisions and rate their quality (1–10 scale)
- Explain mistakes clearly, constructively, and without condescension
- Generate training scenarios adapted to user level and weakness patterns
- Review completed hands and extract strategic lessons
- Track user progress and recurring decision errors
- Adapt all explanations to the user's current skill level (beginner → pro)
- Always distinguish between bad luck and bad strategy

---

## Subagents

| Agent | File | Role |
|-------|------|------|
| Poker Coach | `agents/poker_coach_agent.md` | Main coaching loop, orchestrates all feedback |
| Strategy Analyzer | `agents/strategy_analysis_agent.md` | Evaluates individual decisions (fold/call/raise/bet/check/bluff) |
| Hand Reviewer | `agents/hand_review_agent.md` | Reviews completed hands, identifies key moments |
| Scenario Generator | `agents/scenario_generator_agent.md` | Creates practice situations matched to user level |

---

## Skills

| Skill | File | Domain |
|-------|------|--------|
| Poker Rules | `skills/poker_rules.md` | Texas Hold'em rules, hand rankings, betting rounds, legal actions |
| Poker Strategy | `skills/poker_strategy.md` | Position, ranges, pot odds, bluffing, value betting, board texture |
| Probability Estimation | `skills/probability_estimation.md` | Equity, outs, pot odds, EV calculations |
| Hand Analysis | `skills/hand_analysis.md` | Result-neutral decision evaluation methodology |
| User Coaching | `skills/user_coaching.md` | Teaching methods and communication style by skill level |

---

## Directives (SOPs)

| Directive | File | Trigger |
|-----------|------|---------|
| Analyze Decision | `directives/analyze_player_decision.md` | After each user action |
| Explain Mistake | `directives/explain_mistake.md` | When rating is "mistake" or "blunder" |
| Generate Scenario | `directives/generate_training_scenario.md` | When a new hand is requested |
| Review Hand | `directives/review_completed_hand.md` | After all streets are played |
| Adapt to Level | `directives/adapt_to_user_level.md` | Before any output to the user |

---

## Memory Files

| File | Purpose | Updated |
|------|---------|---------|
| `memory/user_profile.md` | User level, goals, style preferences, format | On profile change |
| `memory/recurring_mistakes.md` | Tracked patterns of repeated errors | After each session |
| `memory/session_history.md` | Summaries of training sessions | After each session |
| `memory/improvement_log.md` | Long-term skill improvement tracking | Weekly |

---

## Execution Scripts (Deterministic Tools)

These scripts do **not** use AI reasoning. They are pure mechanical calculations.

| Script | Purpose | Replaceable With |
|--------|---------|-|
| `execution/hand_evaluator.py` | Evaluate hand strength using 5-card ranking | Full poker solver |
| `execution/odds_calculator.py` | Calculate outs, pot odds, equity, EV | Monte Carlo engine |
| `execution/scenario_engine.py` | Generate structured training scenarios | Curated hand database |
| `execution/decision_logger.py` | Log user decisions to structured records | SQL database |

---

## Context Files

| File | Purpose |
|------|---------|
| `context/poker_terms.md` | Glossary of all terms used by the system |
| `context/supported_game_modes.md` | Available and planned game modes |
| `context/app_constraints.md` | Educational-only constraints, what the app must never do |

---

## Integration Contract

The agent system is called exclusively through `app/backend/services/agent_bridge.py`.

**Inputs to the agent system:**
```json
{
  "operation": "analyze_decision | generate_scenario | review_hand",
  "scenario": { ... },
  "user_action": "fold | check | call | bet | raise",
  "bet_amount": 0,
  "user_level": "beginner | intermediate | advanced | pro",
  "session_id": "uuid"
}
```

**Outputs from the agent system:**
```json
{
  "rating": "good | ok | mistake | blunder",
  "rating_score": 7,
  "explanation": "...",
  "best_alternative": "...",
  "risk_analysis": "...",
  "luck_vs_strategy": "...",
  "recommended_drill": "..."
}
```

**The agent system does not know about HTTP, databases, or UI.**
**The app does not contain poker coaching logic.**

---

## Design Principles

1. **Model-agnostic**: prompt files and SOPs work with any LLM
2. **Deterministic math**: hand evaluation and odds use scripted logic, not AI
3. **Result-neutral analysis**: judge decisions by process, not outcome
4. **Adaptive communication**: always match explanation depth to user level
5. **Constructive feedback**: never shame, always teach
6. **Luck vs strategy**: always separate variance from decision quality

---

## Version

- v1.0 — Texas Hold'em practice mode (heads-up, single hand)
- Focus: flop play, preflop decisions, river calls
