# Directive: Analyze Player Decision

## Purpose

Produce a complete, structured analysis of a single player decision.
This is the most frequently called directive in the system.

---

## Inputs

| Field | Type | Description |
|-------|------|-------------|
| `hole_cards` | List[str] | Player's two hole cards, e.g. `["Ah", "Kd"]` |
| `community_cards` | List[str] | Visible board cards (0–5), e.g. `["Ac", "7h", "2c"]` |
| `pot_size` | float | Total pot before the hero's action |
| `bet_size` | float | Bet/raise the hero is facing (0 if no bet) |
| `hero_stack` | float | Hero's remaining chips |
| `villain_stack` | float | Villain's remaining chips |
| `hero_position` | str | Hero's position (BTN, CO, BB, etc.) |
| `villain_position` | str | Villain's position |
| `street` | str | preflop / flop / turn / river |
| `action_history` | List | All actions taken before this decision |
| `user_action` | str | What the user actually did: fold/check/call/bet/raise |
| `bet_amount` | float or null | If user bet or raised, the amount |
| `user_level` | str | beginner / intermediate / advanced / pro |

---

## Process

### Step 1: Assess Hand Strength
- Call `execution/hand_evaluator.py` → `best_hand(hole_cards, community_cards)` if 5+ cards available
- If fewer than 5 cards (preflop/flop with <5 total), categorize by hand range quality:
  - Premium: AA, KK, QQ, AK
  - Strong: JJ, TT, AQ, AJ, KQ
  - Playable: 99-22, suited connectors, suited aces
  - Marginal/Speculative: offsuit broadways, weak aces
  - Trash: disconnected low cards

### Step 2: Identify Drawing Potential
- Are there flush draws, straight draws, or combo draws?
- Count outs using `execution/odds_calculator.py` → `count_outs_simple()`
- Determine approximate equity using Rule of 2/4

### Step 3: Evaluate Position
- Is hero in position (IP) or out of position (OOP)?
- Does position change the optimal strategy?
  - IP: hero can bet for value more aggressively, control pot size
  - OOP: hero should lean toward check/call or check/raise

### Step 4: Evaluate the User's Action

Map user_action to one of four evaluations:

#### If user_action == "fold"
- Calculate pot odds → if calling was profitable, folding was a mistake
- Check if hand had any showdown value
- Grade: `good` if clearly behind and no pot odds, `mistake` if fold was wrong

#### If user_action == "check"
- Was betting correct? Check if:
  - Hero has the best hand by a significant margin → betting for value
  - Hero has a strong draw → semi-bluffing
  - Hero is acting IP with a strong hand → checking may be trapping (advanced) or missing value (beginner)
- Grade: `good` if checking is part of a valid strategy, `mistake` if clear value was missed

#### If user_action == "call"
- Calculate pot odds and compare to equity
- If equity > pot odds → call was correct (`good`)
- If equity < pot odds by >5% → call was a mistake (`mistake`)
- If borderline → `ok`

#### If user_action == "bet" or "raise"
- Was hero ahead? Was the bet for value or a bluff?
- If value: was sizing appropriate? Too small = `ok`, too large = `ok` or `mistake`
- If bluff: was fold equity sufficient? No fold equity = `blunder`

### Step 5: Identify Best Alternative
- Compare the EV of all available actions
- Pick the highest-EV alternative if the user's action was suboptimal
- State the recommended action AND sizing

### Step 6: Classify Luck vs Strategy
- If the decision was suboptimal: "Strategy mistake. This is within your control."
- If the decision was correct but outcome was bad: "Correct play. The result was variance."
- If it was a cooler (e.g., set over set): "This was unavoidable. Both players played correctly."

### Step 7: Recommend a Drill
Based on the identified weakness, suggest one specific practice area:
- "Practice value betting top pair on dry boards"
- "Practice pot odds calculation before calling"
- "Practice check-raising with draws on wet boards"

### Step 8: Adapt Output to User Level
Apply `directives/adapt_to_user_level.md` before writing the final response.

---

## Outputs

```json
{
  "decision_id": "uuid",
  "rating": "good | ok | mistake | blunder",
  "rating_score": 7,
  "hand_strength": "top pair top kicker",
  "position_note": "Hero is in position (BTN).",
  "recommended_action": "bet",
  "recommended_sizing": "50% pot (50 chips)",
  "explanation": "...",
  "risk_analysis": "...",
  "luck_vs_strategy": "Strategy. Checking here loses EV.",
  "key_concept": "value betting",
  "recommended_drill": "Practice betting top pair in position on dry boards"
}
```

---

## Edge Cases

| Case | Handling |
|------|---------|
| Preflop (no community cards) | Use hand range quality instead of hand evaluator |
| Hero is all-in | Analysis is limited to whether going all-in was correct |
| Very short stack (<10 BBs) | Fold/push decision, use push-fold analysis |
| Multi-way pot | Note that strategy changes multi-way; bluffs are less effective |
| Extremely wet board | Adjust hand strength for draws; note protection value |

---

## Quality Checks

Before returning output, verify:
- [ ] Rating is consistent with the explanation
- [ ] Best alternative is clearly stated with sizing
- [ ] Luck vs strategy is never ambiguous
- [ ] Recommended drill is specific (not just "play better")
- [ ] Explanation is adapted to user level
