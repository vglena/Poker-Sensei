# Directive: Explain Mistake

## Purpose

Explain a player's mistake clearly, constructively, and in a way that builds skill — not frustration.

This directive is invoked when the analysis rating is `mistake` or `blunder`.

---

## Core Principle

A mistake explanation has three jobs:
1. **Name the mistake** without shaming the player
2. **Explain why it was wrong** using the situation, not just general rules
3. **Show the better path** with a concrete action and reason

A good explanation teaches. A bad explanation just grades.

---

## Structure

Every mistake explanation must follow this structure:

### 1. Acknowledge the instinct (when applicable)
If the mistake is understandable, say why someone might make it.
> "It's tempting to check here — you don't want to bet into an ace when you're not sure if villain has one."

### 2. Name the specific error
Be direct. Don't be vague.
> "The problem is that you checked when you held the best hand."
Not: "There may have been a better option available to you."

### 3. Explain the consequence of the mistake
What actually happens when you make this play repeatedly?
> "When you check back top pair in position, you give your opponent a free card. Over many hands, this loses a significant amount of chips."

### 4. State the correct action with reasoning
Not just what — but why.
> "The correct play is to bet about half the pot (50 chips). You have top pair — this is exactly when you want to build the pot. The bet also protects against draws. Villain is likely to call with worse aces, pairs, or draws."

### 5. Note luck vs strategy
> "This is a strategy mistake. The outcome this hand doesn't change the analysis."

### 6. Recommend a drill
One specific, actionable skill to practice.
> "Recommended drill: Value betting top pair. Practice betting 50% pot whenever you have top pair with a good kicker and the opponent checks to you."

---

## Tone Rules

### ALWAYS:
- Frame mistakes as learning opportunities
- Use "the correct play" or "the better option" — not "you should have"
- Acknowledge variance if present
- End with what to practice

### NEVER:
- "You played terribly."
- "Any decent player would have..."
- "Obviously the right move was..."
- "This was a bad decision, period."
- Shame repeated mistakes (log them in memory, adapt scenarios, but don't repeat the shame)

---

## Calibration by User Level

### Beginner Mistake Explanation
Short, plain, one concept:
> "You checked back when you had a strong hand. That's called 'missing value' — you let the opponent see a free card instead of charging them to stay in. Next time, if the opponent checks to you and you have the top pair, try betting about half the pot."

### Intermediate Mistake Explanation
Include strategy concepts by name:
> "Checking back TPTK in position on a dry board is a common leak. Without a bet, you give draws a free card and miss value from worse aces. A 50–66% pot c-bet is standard here. Your range advantage on A-high dry boards supports betting wide."

### Advanced Mistake Explanation
Include range and EV framing:
> "Checking back TPTK here weakens your in-position betting range. On A72r, your range connects much better than villain's BB defending range. Not betting your entire top pair segment at high frequency leaves EV on the table and over-protects your checking range unnecessarily."

### Pro Mistake Explanation
Dense, technical, no hand-holding:
> "TPTK on A72r is a clear bet in a position-vs-BB context. Solver output supports ~80%+ bet frequency for TPTK here. Checking back creates a range protection argument only if you're under-bluffing in your check-back range — if you're already balanced, checking TPTK is a leak."

---

## Examples

### Example 1: Over-folding to a Bluff
```
Rating: mistake (3/10)

You folded a pair of queens to a small river bet. Let's look at what happened.

The problem is that you folded too quickly. When someone bets small on the river (33% pot), they often have a draw that missed — not a strong hand. Strong hands usually bet bigger to get value.

The correct play here was to call. You have second pair, and the bet size was small enough that you only need 25% equity to break even. A pair of queens beats many bluffs.

Over time, folding to every small bet trains your opponents to exploit you. If they know you fold pairs to small bets, they'll bluff you endlessly.

Luck vs Strategy: Strategy. This was a fold-too-much situation.

Recommended Drill: Practice calling small river bets when you have a showdown-value hand. Look for bet sizes under 40% pot — these usually require less equity to call profitably.
```

### Example 2: Bluffing a Calling Station
```
Rating: blunder (1/10)

You bluffed four streets against an opponent who has called every bet this hand.

Bluffing requires fold equity — the chance that your bet will make the opponent fold. In this situation, the opponent has shown no signs of folding. They called preflop, flop, and turn.

The correct play was to check or give up. Bluffing someone who doesn't fold loses money every single time.

Luck vs Strategy: Pure strategy error. This wasn't variance — this was bluffing the wrong person.

Recommended Drill: Opponent modeling. Before bluffing, ask yourself: "Does this person fold?" If not, find a different line.
```
