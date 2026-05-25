# Directive: Review Completed Hand

## Purpose

Review a full hand from preflop to showdown (or to fold).
Identify the key decision point, all mistakes and good moves, and the primary lesson.

---

## Inputs

```json
{
  "hand_id": "uuid",
  "session_id": "uuid",
  "hole_cards": ["Ah", "Kd"],
  "community_cards": ["Ac", "7h", "2c", "Kc", "9s"],
  "streets": { ... },
  "showdown": { ... },
  "user_level": "beginner"
}
```

Full schema is defined in `agent/agents/hand_review_agent.md`.

---

## Process

### Step 1: Reconstruct the Hand

Read the `streets` field and build a complete timeline:
1. Preflop: what happened, who was the aggressor, what were the stack/pot sizes?
2. Flop: what were the community cards, what were the actions?
3. Turn: same
4. River: same
5. Showdown: who won, what did each player have?

### Step 2: Evaluate Each Decision Point

For each moment where the hero had to act, apply `directives/analyze_player_decision.md`.
Record the grade for each action.

Do not spend equal time on every action — weight toward decisions that were most consequential.

### Step 3: Find the Key Decision

The key decision is the action that had the highest impact on the outcome.

Identify this by asking:
- Which decision had the largest EV difference between the optimal play and what was done?
- Which decision most directly caused the final result?
- Was there a moment where the hero should have ended the hand (folded)?

### Step 4: Classify the Outcome

Use the classification from `skills/hand_analysis.md`:
- `strategy_win`: hero played well and won
- `strategy_loss`: hero made mistakes that contributed to the loss
- `luck_win`: hero played suboptimally but won
- `luck_loss`: hero played correctly but lost (variance/cooler)
- `mixed`: combination of strategy and variance

### Step 5: Construct the Primary Lesson

Do not list every mistake. Choose ONE primary lesson that, if learned, would have most improved the outcome.

Format: "[Concept name]. [When to apply it]. [What it prevents]."

Example:
> "Turn protection betting. When you have two pair on a wet board, bet to deny free cards to flush and straight draws. This prevents losing to a draw that you could have charged."

### Step 6: Recommend a Drill

One specific drill based on the primary lesson.

### Step 7: Adapt to User Level

Apply `directives/adapt_to_user_level.md` before writing the final review output.

---

## Output

```json
{
  "hand_id": "uuid",
  "outcome": "loss",
  "outcome_classification": "mixed",
  "key_decision": {
    "street": "turn",
    "hero_action": "check",
    "optimal_action": "bet for value and protection",
    "sizing_recommendation": "60–75% pot",
    "explanation": "Two pair on a wet board should bet to deny free cards."
  },
  "street_grades": {
    "preflop": {
      "rating": "ok",
      "score": 7,
      "note": "Calling AKo vs a raise from CO is standard."
    },
    "flop": {
      "rating": "ok",
      "score": 6,
      "note": "Calling top pair vs a bet was fine; raising would have been better."
    },
    "turn": {
      "rating": "mistake",
      "score": 3,
      "note": "Two pair on a wet board should bet. The free card let villain complete the flush."
    },
    "river": {
      "rating": "ok",
      "score": 5,
      "note": "The call was marginal. With two pair vs a big bet, it's defensible."
    }
  },
  "luck_vs_strategy": "The flush completing was partly variance, but the free card was a strategy error. 60% strategy, 40% variance.",
  "primary_lesson": "Bet two pair on wet boards. Don't give free cards when you're ahead and there are draws out there.",
  "recommended_drill": "Turn bet sizing with two pair on boards with flush or straight draws.",
  "overall_grade": "ok",
  "overall_score": 5
}
```

---

## Common Hand Patterns

| Pattern | Key Mistake | Primary Lesson |
|---------|------------|---------------|
| Check two pair → flush hits | Missed protection bet | Bet for value AND protection |
| Call preflop → miss board → call bet anyway | Continuing with no equity | Know when to give up post-flop |
| Value bet river → villain raises → hero calls | Calling without considering villain's range | River raises are almost always value |
| Bluff river after checking twice | No credibility for bluff | Aggression must be consistent across streets |
| Fold top pair to small bet | Over-folding | Calculate pot odds before folding |

---

## Quality Checklist

Before returning:
- [ ] Key decision is clearly identified
- [ ] All streets have a grade and note
- [ ] Outcome classification is `strategy_win | strategy_loss | luck_win | luck_loss | mixed`
- [ ] Primary lesson is specific (not "play better")
- [ ] Luck vs strategy is clearly separated
- [ ] Language is adapted to user level
- [ ] Recommended drill is actionable
