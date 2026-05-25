# Poker Training App

A local training tool for learning Texas Hold'em poker strategy.
Practice real scenarios, make decisions, get instant coaching feedback.

> **This is NOT a gambling app. Not a multiplayer app. Not for playing with real money.**
> It is a single-player study tool — like a chess tactics trainer, but for poker.

---

## First Working Flow

1. User opens the practice screen
2. App requests a training scenario from the backend
3. User reads the situation (hole cards, board, pot, position) and chooses an action
4. App sends the decision to the backend
5. Backend asks the agent system to analyze the decision
6. Agent returns coaching feedback:
   - **Decision rating** (Good / Acceptable / Mistake / Blunder)
   - **Score** (1–10)
   - **Explanation** of why the play is correct or not
   - **Best alternative** — what the optimal play was
   - **Luck vs. strategy** — is this outcome under the player's control?
   - **Recommended drill** — targeted practice for this weakness
7. App displays the full analysis
8. Session data saved to memory

---

## Architecture

```
poker/
├── agent/          ← Poker coaching brain (model-agnostic)
│   ├── agents/     ← Subagent definitions (Markdown SOPs)
│   ├── skills/     ← Domain knowledge (rules, strategy, probability)
│   ├── directives/ ← Process SOPs (analyze_decision, generate_scenario, ...)
│   ├── memory/     ← User profiles, session history, mistake log
│   ├── context/    ← Glossary, game modes, constraints
│   └── execution/  ← Deterministic Python scripts
│
└── app/            ← User-facing application
    ├── shared/     ← Pydantic schemas + TypeScript types
    ├── backend/    ← FastAPI server
    │   ├── routers/    ← /scenario, /decision, /session
    │   └── services/   ← ScenarioService, AgentBridge
    └── frontend/   ← React + TypeScript + Vite
        └── src/
            ├── api/        ← Fetch client
            ├── components/ ← PokerTable, ActionButtons, FeedbackPanel, ...
            ├── types/      ← TypeScript interfaces
            └── styles/     ← Dark felt-themed CSS
```

**Key separation principle:** The `app/` layer never imports directly from `agent/`.
All agent interaction goes through `app/backend/services/agent_bridge.py`.

---

## Tech Stack

| Layer    | Technology                  |
|----------|-----------------------------|
| Frontend | React 18 + TypeScript + Vite |
| Backend  | FastAPI + Pydantic v2        |
| Agent v1 | Rule-based heuristics (no LLM required) |
| Storage  | JSON Lines (`.jsonl`) per session |
| Cards    | Deterministic hand evaluator (pure Python) |

---

## Setup

### Backend

```bash
cd app/backend
pip install -r requirements.txt
uvicorn main:app --reload
# API available at http://localhost:8000/api
```

### Frontend

```bash
cd app/frontend
npm install
npm run dev
# App available at http://localhost:5173
```

The Vite dev server proxies `/api` to `http://localhost:8000` automatically.

---

## Agent System

The coaching brain lives entirely in `/agent` and is model-agnostic.

Version 1 uses rule-based heuristics (`agent_bridge.py → _rule_based_analysis()`).
To connect an LLM, replace that single function — nothing else changes.

### Execution Scripts (pure Python, no AI dependencies)

| Script | Purpose |
|--------|---------|
| `hand_evaluator.py` | 5-card hand ranking, preflop classification |
| `odds_calculator.py` | Outs, pot odds, equity, EV |
| `scenario_engine.py` | Generates practice scenarios |
| `fixtures.py` | 5 hand-crafted, named training scenarios |
| `decision_logger.py` | JSON Lines session logging |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/health` | Health check |
| GET    | `/api/scenario/new` | Get a new generated training scenario |
| GET    | `/api/scenario/fixture/{name}` | Get a named stable fixture scenario |
| GET    | `/api/scenario/example` | Get the static example scenario |
| POST   | `/api/decision/analyze` | Submit decision (logs + analyzes) |
| POST   | `/api/analyze` | Analyze decision (stateless, no logging) |
| POST   | `/api/hand/review` | Full hand review |
| POST   | `/api/session/save` | Save session summary |
| GET    | `/api/session/{id}/summary` | Retrieve rich session report |

#### Available fixture names

| Name | Scenario |
|------|---------|
| `preflop_raise` | A♠K♠ facing CO open on BTN — fold, call, or 3-bet? |
| `flop_cbet` | K♥Q♥ top two pair on dry K♦8♣3♠ — check or c-bet? |
| `turn_draw` | 9♦T♦ open-ended draw facing a bet on the turn |
| `river_bluff_catch` | A♣J♦ top pair facing a large river bet — call or fold? |
| `value_bet_sizing` | Q♠Q♣ top set on Q♦J♣5♥ — how much to bet? |

---

## Card Notation

Cards are 2-character strings: rank + suit.

- Ranks: `2 3 4 5 6 7 8 9 T J Q K A`
- Suits: `c` (clubs) `d` (diamonds) `h` (hearts) `s` (spades)

Examples: `Ah` = Ace of hearts, `Kd` = King of diamonds, `Tc` = Ten of clubs

---

## Version 1 Training Loop

This is the full flow from user action to coaching feedback and session summary:

```
1. User selects a scenario
   ├── Random: GET /api/scenario/new?difficulty={level}
   └── Named drill: GET /api/scenario/fixture/{name}
       └── Frontend fetches fixture list first: GET /api/scenario/fixtures

2. User reads the situation and makes a poker decision
   └── PokerTable displays hole cards, board, pot, stacks, position
       ActionButtons shows only the legal actions for this scenario

3. Backend validates the action
   └── POST /api/decision/analyze
       └── agent_bridge.validate_action_legality()
           ├── If illegal → returns rating=blunder, score=1 (always displayable)
           └── If legal → proceeds to analysis

4. Agent bridge analyzes the decision
   └── agent_bridge.analyze_decision()
       ├── hand_evaluator.py — evaluates hero's hand strength
       ├── odds_calculator.py — calculates pot odds and equity
       ├── _rule_based_analysis() — generates full DecisionAnalysis
       │   ├── rating (good / ok / mistake / blunder)
       │   ├── rating_score (1–10)
       │   ├── explanation + best_alternative + recommended_drill
       │   └── mistake_category (passive_play, missed_value, sizing_error, ...)
       └── Returns DecisionAnalysis to the router

5. Decision is logged
   └── decision_logger.create_decision_record()
       └── Appended to agent/memory/logs/decisions_{session_id}.jsonl
           Fields logged: street, action, rating, score, mistake_category,
                          explanation_summary, recommended_action

6. Frontend displays coaching feedback
   └── FeedbackPanel shows:
       ├── Score + rating badge + mistake category tag
       ├── Analysis + better play + sizing
       ├── Context (hand strength, position, risk)
       ├── Luck vs. strategy note
       ├── Key concept
       └── Recommended drill

7. SessionReport summarizes progress (on demand)
   └── GET /api/session/{id}/summary
       └── agent_bridge.get_session_summary()
           ├── Reads all DecisionRecords from the session log
           ├── Computes: total, avg score, accuracy %, strongest/weakest
           ├── Identifies recurring mistake_category
           └── Returns SessionReport with recommended_drill + progress_note
```

**Architecture rule:** React components display state and fire actions.
The backend orchestrates. The `/agent` system contains all strategy reasoning.

---

## Testing

```bash
cd app/backend
pip install pytest httpx
pytest tests/ -v
```

Tests cover: fixture list (5 scenarios), fixture loading, invalid action handling,
`mistake_category` in analysis response, session 404 for unknown sessions, health check.

---

## Design Principles

- **Strategy focus:** Players learn decision-making, not gambling.
- **No live AI required:** v1 runs fully offline with rule-based coaching.
- **Stateless API:** Each request includes the full scenario — no server-side session cache.
- **Modular:** Agent system and application are fully decoupled.
- **Extensible:** Adding new streets, game modes, or LLM providers requires minimal changes.

