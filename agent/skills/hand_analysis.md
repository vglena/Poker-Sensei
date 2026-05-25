# Skill: Hand Analysis

## Overview

This skill defines how to evaluate a poker hand or decision without being biased by the final result.

The core principle: **judge the decision by the process, not the outcome.**

A good decision can lose. A bad decision can win. The analysis must be result-neutral.

---

## Result-Neutral Evaluation

### The Fundamental Error: Resulting

"Resulting" is judging a decision based on what happened, not what was optimal.

❌ "You should have folded because villain had a set."
✅ "At the time of your call, villain could have many worse hands. The call was correct."

❌ "Your bluff was brilliant — it worked!"
✅ "Your bluff had low fold equity against a calling station. It succeeded this time due to variance."

### The Standard: What Would an Optimal Player Do?

Evaluate every decision against this question:
> What is the play that maximizes EV given the information available at the time of the decision?

---

## The Analysis Process

### Step 1: Freeze the Frame
Analyze only what was known at the moment of the decision:
- Visible cards (hole cards + community cards)
- Pot size
- Stack sizes
- Position
- Action history (what happened before this decision)
- Villain's likely range based on that action history

Do NOT use information that came after the decision point.

### Step 2: Identify the Realistic Villain Range
Based on the action history, what hands could villain realistically have?
- What range did they open/call/raise preflop?
- How does the board interact with that range?
- What does their current action (bet/check/raise) suggest about their holding?

### Step 3: Evaluate Hero's Options
For each available action (fold, check, call, bet, raise):
- What is the approximate EV?
- What is the risk/reward profile?
- How does this action interact with the villain's likely range?

### Step 4: Identify the Best Action
The best action is the one with the highest EV, accounting for:
- Probability of being ahead
- Size of pot if you win
- Size of loss if you're behind
- Fold equity (if betting or raising)
- Implied odds (if calling with a draw)

### Step 5: Rate the Decision
Compare what the hero did to the best action:
- Same action → `good` (8–10)
- Close alternative → `ok` (5–7)
- Suboptimal but understandable → `mistake` (2–4)
- Clearly wrong, loses EV significantly → `blunder` (1)

---

## Common Analysis Patterns

### Pattern: Passive with a Strong Hand
- Symptom: checking/calling when you should bet/raise
- Result: missing value, letting draws hit for free
- Category: strategy mistake
- Lesson: when you have the best hand, build the pot

### Pattern: Bluffing into a Calling Station
- Symptom: betting when opponent has low fold frequency
- Result: losing chips to a worse hand that called
- Category: strategy mistake (opponent modeling failure)
- Lesson: bluffs need fold equity; check when opponent won't fold

### Pattern: Folding the Best Hand
- Symptom: folding when pot odds or equity justified a call
- Result: losing the pot you should have won
- Category: strategy mistake
- Lesson: calculate pot odds before folding to a bet

### Pattern: Over-valuing a Hand
- Symptom: calling or raising without considering the full range villain can have
- Result: paying off a stronger hand
- Category: strategy mistake
- Lesson: strong hands can still be behind; think about villain's range, not just your cards

### Pattern: Losing to Variance (Not a Mistake)
- Symptom: played correctly but lost to a suckout or cooler
- Example: AA vs KK, K on river
- Category: variance (luck)
- Lesson: maintain the same strategy. Over time, AA vs KK is very profitable.

---

## Luck vs Strategy Classification

Every outcome must be classified:

| Classification | Criteria |
|---------------|----------|
| **Strategy mistake** | Hero deviated from the EV-maximizing play |
| **Correct play, bad outcome** | Hero made the optimal play but variance caused a loss |
| **Cooler** | Both players played optimally; the outcome was determined by card distribution |
| **Mixed** | Hero made some mistakes AND had some variance component |

### How to Identify a Cooler
A cooler is when:
- You cannot fold (AA vs KK preflop, top set vs flush draw on the flop)
- The equity difference was small at the time of the key decision
- A reasonable player would make the same decision every time

---

## Board Analysis Shortcuts

### Who Hits This Board?
Quickly identify whose range benefits from the board:

- Low boards (2-7): benefits blinds and wide callers
- High boards (A-K-Q): benefits preflop raisers with strong ranges
- Connected boards (T-J-Q): benefits suited connectors from any range
- Paired boards: benefits anyone who called with that pair rank

### Texture Classification

| Texture | Definition | Strategic Impact |
|---------|-----------|-----------------|
| Dry | No flush or straight draws possible | Smaller bets, less protection needed |
| Wet | Many draws possible | Larger bets, protection value |
| Coordinated | Board has straights and flushes | Draws have high equity |
| Rainbow | 3 different suits | Flush draws impossible |
| Monotone | 3 cards same suit | Flush draws present, opponent may already have a flush |
