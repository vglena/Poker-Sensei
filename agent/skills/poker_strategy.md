# Skill: Poker Strategy

## Overview

This skill defines poker strategy concepts from beginner to advanced.
The agent uses this skill to identify what the correct play is and why.

---

## Foundational Concepts

### Position is Everything

Being in position (acting last) is the most consistent edge in poker.
- You have more information before you act
- You control pot size more effectively
- Bluffs are more profitable in position

**Positional tiers** (best to worst postflop):
1. BTN (best) — always last to act
2. CO
3. HJ
4. MP / UTG+1
5. UTG
6. BB (worst postflop — always acts first)

**Teaching rule**: When a hero checks back in position with a strong hand, they are usually making a mistake. When a hero bets out of position into a polarized range, they are often making a mistake. Position determines both.

---

## Preflop Strategy

### Hand Selection Basics

Strong hands: AA, KK, QQ, JJ, AK (always raise or re-raise)
Good hands: TT, 99, AQ, AJs+, KQs (raise from most positions)
Speculative hands: 77-22, suited connectors, suited aces (raise or call in position)
Marginal hands: K9o, Q8o, J7s (open from late position only)
Trash: 72o, 83o (fold almost always)

### 3-Betting (Re-raising Preflop)

3-bet range should be:
- **Value**: hands that dominate the opener's range (AA, KK, QQ, AK)
- **Bluffs**: hands with good blockers or suited connectors that play well post-flop

The mistake most beginners make: only 3-betting with the nuts. This makes you too predictable.

### Calling vs 3-Betting

Call when: you have a good hand but 3-betting may not build more value (e.g., JJ vs early position raise)
3-bet when: you have a hand that beats most of the opener's range or you want to isolate

---

## Postflop Strategy

### C-Betting (Continuation Bet)

A c-bet is betting on the flop after being the preflop aggressor.

**When to c-bet:**
- You hit the board (top pair, overpair, draw)
- You have range advantage (your range hits this board more often than villain's)
- The board is dry (opponent has fewer strong hands)

**When NOT to c-bet:**
- You have very little equity (total air on a board that favors villain)
- Villain is unlikely to fold (e.g., BB who has called out of position with a wide range on a low board they smash)
- Pot is large and your hand is marginal

### Bet Sizing

| Situation | Sizing |
|-----------|--------|
| Thin value on dry board | 33–50% pot |
| Strong hand, some draws present | 50–75% pot |
| Polarized range (strong or air) | 75–100% pot |
| River value bet | 50–80% pot |
| Pot-building bet | 33% pot (small ball) |

**Key insight**: smaller bets require less fold equity. Larger bets need more equity or stronger hands.

---

## Drawing Hands

### What is a Draw?

A hand that is not currently the best but can become the best hand:
- **Flush draw**: 4 cards of the same suit (9 outs)
- **Open-ended straight draw (OESD)**: 4 consecutive cards (8 outs)
- **Gutshot**: 4 cards with one gap (4 outs)
- **Combo draw**: flush draw + straight draw (up to 15 outs)

### Playing Draws

**Semi-bluffing**: betting or raising with a draw. Profitable when:
- You can win by making opponent fold OR by hitting your draw
- EV of semi-bluff > EV of passive play

**Drawing passively**: calling with a draw. Correct when:
- Pot odds justify the call (see probability_estimation skill)
- Stack sizes make raising dangerous
- Board is dry (semi-bluff has low fold equity)

---

## Bluffing

### When Bluffing is Profitable

EV(bluff) > 0 when:
`fold_equity × pot > (1 - fold_equity) × amount_risked`

**Bluffing conditions:**
- Opponent's range is wide (many hands that can fold)
- Board texture changed (missed draws on river)
- You have position (more likely villain will fold to pressure)
- You have blockers (holding A♠ blocks opponent from having the nut flush)

### When NOT to Bluff

- Villain is a calling station (never folds)
- Your hand has showdown value (thin value beat is better than bluffing)
- Multiple opponents (bluffs rarely work multi-way)
- You are out of position with no fold equity

---

## Value Betting

### The Core Principle

Bet when you expect to be called by worse hands more often than by better hands.

**Thin value bet**: betting with a hand that beats a narrow range (e.g., second pair, top pair with weak kicker)
**Thick value bet**: betting with a hand that beats a wide range (e.g., set, two pair)

### Common Value Betting Mistakes

| Mistake | Description |
|---------|-------------|
| Checking back strong hands | Missing value out of fear |
| Betting too small for value | Opponent calls but you get less |
| Betting too large for value | Opponent folds hands you beat |
| Value betting into a range that beats you | Turning value into a bluff |

---

## Board Texture

### Wet Boards (Many Draws)
Example: T♥9♥8♦
- Many flush and straight draws possible
- Strong hands should bet for value AND protection
- Draws should semi-bluff often
- Calling stations are very dangerous here

### Dry Boards (Few Draws)
Example: A♣7♥2♠
- Few draws possible
- Smaller bets work well for value
- Opponents are unlikely to have strong draws
- You can be more "relaxed" about opponents catching up

### Paired Boards
Example: T♥T♣7♠
- Sets and boats are strong
- Trips are possible for both players
- Value betting is riskier (opponent can have you beat)

### Connected Boards
Example: J♠T♥9♦
- Many straight possibilities
- Fold equity is low (too many draws)
- Overpairs lose a lot of equity here

---

## Opponent Modeling (Version 1 — Basic Profiles)

For version 1, model opponents as one of these types:

| Type | Description | Exploit |
|------|-------------|---------|
| Fish | Calls too much, bluffs rarely | Value bet thin, bluff rarely |
| Nit | Folds too much, only plays strong hands | Bluff more, fold to their raises |
| Aggressor | Bets and raises frequently | Call down more, trap with strong hands |
| Balanced | Hard to exploit | Play fundamentals, look for leaks |

---

## Mistake Categories

When analyzing a player's decision, classify errors using one of these canonical categories.
These categories are stored in `DecisionRecord.mistake_category` and surfaced in session reports.

| Category | Code | Description | Common Cause |
|----------|------|-------------|--------------|
| Passive play | `passive_play` | Hero fails to bet or raise with a hand that should be aggressive. Checking back top pair on a wet board, limping with premium hands, etc. | Fear of raises; uncertainty about hand strength |
| Missed value | `missed_value` | Hero had the best hand but bet too small or checked, leaving money in the pot. | Over-caution; not recognizing hand strength |
| Hand selection | `hand_selection` | Hero played a hand that should have been folded preflop, or folded a hand that was clearly profitable to continue with. | Misunderstanding of range fundamentals |
| Over-bluffing | `over_bluff` | Hero bluffed too often, too large, or in a spot where villain is unlikely to fold. | Incorrect fold equity estimation; tilt |
| Calling station | `calling_station` | Hero called too often with weak holdings, ignoring clear signs of villain's strength. | Not folding to pressure; pot commitment bias |
| Sizing error | `sizing_error` | Hero made the right action type (bet/raise) but the size was clearly too large or too small for the situation. | Not adapting bet size to board texture or stack depth |
| General mistake | `general_mistake` | Error doesn't fit cleanly into another category. Catch-all for minor strategic errors. | Various |

### Assignment Logic (for `agent_bridge._rule_based_analysis()`)

Use the following mapping from `key_concept` to `mistake_category`:

```
key_concept keyword → mistake_category
---------------------------------------
"3-bet" or "aggression" or "raise" → passive_play  (if hero checked or called)
"value" or "bet sizing" → missed_value or sizing_error
"hand selection" or "preflop" → hand_selection
"bluff" or "semi-bluff" → over_bluff
"pot odds" or "calling" → calling_station
"sizing" or "bet size" → sizing_error
(default) → general_mistake
```

### Coaching Tone by User Level

When writing the coaching explanation for a mistake, adapt the depth:

| Level | Explanation depth |
|-------|-------------------|
| beginner | Simple and direct. State the correct play, explain why in one sentence. Avoid jargon. |
| intermediate | Include the reasoning. Mention range concepts, pot odds if relevant. One example. |
| advanced | Full analysis. Discuss EV, range dynamics, exploitability. Reference balance if relevant. |
| pro | Concise. Assume full conceptual understanding. Focus on edge cases and solver-like reasoning. |

