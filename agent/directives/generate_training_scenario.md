# Directive: Generate Training Scenario

## Purpose

Produce a structured, valid poker practice scenario.
Scenarios have a hidden learning objective revealed after the user acts.

---

## Inputs

| Field | Type | Description |
|-------|------|-------------|
| `user_level` | str | beginner / intermediate / advanced / pro |
| `focus_area` | str or null | Optional: specific skill to target |
| `street_preference` | str or null | Optional: preflop / flop / turn / river |
| `recurring_mistakes` | List[str] | Patterns from `memory/recurring_mistakes.md` |
| `seed` | int or null | For reproducible scenarios |

---

## Process

### Step 1: Select Street

If `street_preference` is provided, use it.
Otherwise, weight streets based on user level:
- Beginner: 30% preflop, 50% flop, 20% river
- Intermediate: 20% preflop, 40% flop, 25% turn, 15% river
- Advanced: 15% preflop, 30% flop, 30% turn, 25% river
- Pro: 10% preflop, 25% flop, 35% turn, 30% river

### Step 2: Select Learning Objective

If `focus_area` is provided, use it.
If recurring mistakes exist, weight toward those weaknesses:
- `passive_with_strong_hands` → value betting scenarios
- `over_folding` → calling with pot odds scenarios
- `over_bluffing` → scenarios where checking is correct
- `ignoring_position` → position-dependent spots

Default objectives by level:

| Level | Default Objective |
|-------|-----------------|
| Beginner | Value betting top pair |
| Intermediate | Bet sizing for draws |
| Advanced | Check-raise vs bet range construction |
| Pro | Mixed strategy frequency decisions |

### Step 3: Deal Cards

Call `execution/scenario_engine.py` → `generate_scenario(difficulty, street, seed)`

Validate:
- No duplicate cards
- Cards make the learning objective achievable
- Board texture matches the scenario intent
  - Value bet scenario → hero must have a strong hand (top pair or better)
  - Draw scenario → hero must have a draw (flush/straight)
  - Bluff catch → hero must have a marginal made hand

### Step 4: Construct Action History

Build a realistic prelude of actions:

| Street | Typical Setup |
|--------|--------------|
| Preflop | Villain raised, hero can fold/call/3bet |
| Flop | Villain checked to hero (value spot) OR villain bet (decision spot) |
| Turn | Both checked flop, now there's a decision |
| River | Villain bets into hero (call/raise/fold decision) |

Keep action history minimal for beginner scenarios.
Add complexity for advanced scenarios (e.g., hero raised flop, villain called, now on turn).

### Step 5: Set Available Actions

| Situation | Available Actions |
|-----------|-----------------|
| No bet facing hero | check, bet |
| Bet facing hero | fold, call, raise |
| Preflop, hero in blind | fold, call, raise |

### Step 6: Set Bet Sizing Options

| User Level | Sizing Options |
|-----------|---------------|
| Beginner | 3 options: 33%, 50%, 75% of pot |
| Intermediate | 4 options: 25%, 33%, 50%, 75%, 100% of pot |
| Advanced/Pro | Full slider: any amount from min to max |

### Step 7: Add Hidden Learning Objective

Record the learning objective and do NOT reveal it to the user until after they act.
After the user acts, the analysis will reference this objective.

---

## Output

```json
{
  "scenario_id": "uuid",
  "street": "flop",
  "hole_cards": ["Ah", "Kd"],
  "community_cards": ["Ac", "7h", "2c"],
  "pot_size": 100,
  "hero_stack": 900,
  "villain_stack": 900,
  "hero_position": "BTN",
  "villain_position": "BB",
  "action_history": [
    {"player": "villain", "action": "check", "amount": null}
  ],
  "available_actions": ["check", "bet"],
  "bet_sizing": {
    "min_bet": 25,
    "max_bet": 900,
    "common": [33, 50, 75]
  },
  "learning_objective": "value betting top pair top kicker on a dry board",
  "difficulty": "beginner",
  "tags": ["flop", "value-bet", "top-pair", "dry-board", "in-position"]
}
```

---

## Validation Rules

Before returning a scenario:
- [ ] hole_cards and community_cards have no duplicates
- [ ] Total unique cards ≤ 7
- [ ] `available_actions` matches the game state
- [ ] `pot_size` > 0
- [ ] `hero_stack` > 0
- [ ] `learning_objective` is specific (not "play poker better")
- [ ] At least one action in `available_actions` is clearly correct

---

## Example Scenario Catalog

### Beginner: Value Bet Spot
- Hero: A♠K♦ (TPTK)
- Board: A♣7♥2♦ (dry, rainbow)
- Villain: checks
- Correct action: bet 50%
- Learning: bet your strong hands for value

### Intermediate: Pot Odds Draw Call
- Hero: 8♥9♥ (flush draw + gutshot)
- Board: 7♥K♣2♥ (flush draw)
- Villain: bets 50 into 100
- Correct action: call (35% equity > 33% required)
- Learning: calculate and use pot odds

### Advanced: Turn Bluff with Equity
- Hero: J♦T♦ (OESD on a board with two diamonds)
- Board: Q♦9♠3♦A♠ (missed straight, picked up flush draw)
- Villain: checks
- Correct action: bet (semi-bluff with 9-15 outs)
- Learning: semi-bluff on turns when you pick up equity

### Beginner: Do Not Bluff
- Hero: 4♣5♣ (missed flush draw)
- Board: A♥K♣9♦7♠2♣ (missed completely)
- Villain: bets small (33% pot)
- Correct action: fold (no equity, no fold equity if raised)
- Learning: do not bluff with nothing; fold and move on
