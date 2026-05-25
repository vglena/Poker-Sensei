# Skill: Probability Estimation

## Overview

This skill defines how the system should estimate equity, outs, pot odds, and expected value.
These calculations are deterministic and should be confirmed by the execution scripts in `execution/`.

---

## Outs

An **out** is a card that improves your hand to (likely) the best hand.

### Common Out Counts

| Draw | Outs | Example |
|------|------|---------|
| Flush draw | 9 | 4 hearts, 9 hearts remain |
| Open-ended straight draw | 8 | 5-6-7-8, need 4 or 9 |
| Two overcards | 6 | AK on J-7-2 board |
| Gutshot straight | 4 | 5-6-8-9, need 7 |
| One overcard | 3 | K on J-7-2 board |
| Pair to trips | 2 | Pair, need third card |
| Flush draw + OESD | 15 (approx) | Combo draw |
| Set to full house or quads | 7 | Three of a kind |

### Discount Outs

Some "outs" may improve your hand but also improve the opponent's hand. These are **tainted outs**.

Example: You have 7♦8♦ on a board of 9♦T♣2♥. A J gives you a straight but may also give an opponent a higher straight if they have QJ or KQ.

When counting outs, be conservative. If an out may give the opponent a stronger hand, discount it by 50%.

---

## The Rule of 2 and 4

A fast mental shortcut for equity estimation:

| Situation | Multiply outs by |
|-----------|-----------------|
| One card to come (turn → river) | × 2 |
| Two cards to come (flop → river) | × 4 |

**Example**: 9 flush outs with two cards to come → 9 × 4 = ~36% equity

This is an approximation. The exact formula is:
- One card: `outs / unseen_cards × 100`
- Two cards: `1 - ((unseen - outs) / unseen) × ((unseen - outs - 1) / (unseen - 1)) × 100`

For version 1, use the Rule of 2 and 4 for explanations. The execution script handles exact values.

---

## Pot Odds

**Pot odds** tell you how much equity you need to make a call profitable.

### Formula

```
pot_odds = call_amount / (pot_size + call_amount)
```

This gives you the **minimum equity** needed to break even on a call.

### Example

Pot = 100. Villain bets 50. You must call 50.
```
pot_odds = 50 / (100 + 50) = 50 / 150 = 33.3%
```

You need at least 33.3% equity to break even on a call.

If you have a flush draw (≈36% equity with one card to come), the call is profitable.
If you have a gutshot (≈8% equity with one card to come), the call is not profitable.

### Quick Reference Table

| Bet Size (% of pot) | Required Equity |
|---------------------|-----------------|
| 25% pot | 20% |
| 33% pot | 25% |
| 50% pot | 33% |
| 75% pot | 43% |
| 100% pot (pot-size bet) | 50% |
| 150% pot | 60% |

---

## Implied Odds

When the pot odds alone don't justify a call, **implied odds** may make it correct.

Implied odds account for additional chips you expect to win if you hit your hand.

### When Implied Odds are High
- Deep stacks (more money behind)
- Opponent has a strong hand that will pay you off
- You are in position

### When Implied Odds are Low
- Short stacks
- Board is obvious when you hit (opponent can easily see your flush)
- Opponent is a nit who will fold if you hit

### Rule of Thumb for Implied Odds

For set mining (calling with a pocket pair to flop a set):
- You need approximately 10-15× the call amount in effective stacks to justify the call
- Example: Call 20 chips → need ~200-300 chips in stacks behind

---

## Expected Value (EV)

**EV** = the average chips won (or lost) per action over many repetitions.

### Formula

```
EV = (P_win × win_amount) - (P_lose × lose_amount)
```

### Example

You're considering a river bluff:
- You bet 60 into 100 pot
- You estimate opponent folds 50% of the time
- If called, you lose 60 (you have a missed draw)

```
EV(bluff) = (0.50 × 100) - (0.50 × 60) = 50 - 30 = +20
```

The bluff has +EV. Do it.

### EV vs Variance

A play can be +EV and still lose money in the short run (high variance).
A play can be -EV and win money in the short run (lucky outcome).

**The system must always evaluate based on EV, not results.**

---

## Equity vs Hand Strength

- **Hand strength**: how strong is my hand right now?
- **Equity**: how often do I win at showdown if all money goes in right now?

These are different. A nut flush draw on the flop has low hand strength (not yet made) but high equity (~36% if opponent has one pair).

The coaching system must distinguish:
- "Your hand is weak but your equity is good" → may justify a call
- "Your hand looks strong but your equity is low" → may be vulnerable to draws

---

## Fold Equity

**Fold equity** = the portion of EV gained by making opponents fold.

Aggressive plays (bets and raises) gain fold equity. Passive plays (checks and calls) have zero fold equity.

```
fold_equity_EV = P(fold) × current_pot
```

Semi-bluffs derive EV from both fold equity and draw equity.
