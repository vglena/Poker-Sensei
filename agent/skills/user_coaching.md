# Skill: User Coaching

## Overview

This skill defines how to adapt poker explanations to different user levels.
The same concept must be explained differently to a beginner vs a pro.

The coaching system must never:
- Talk down to users
- Use jargon with beginners without explanation
- Over-simplify concepts for advanced users
- Give the same feedback template regardless of level

---

## User Levels

### Beginner
**Profile**: Knows the basic rules, can identify hand rankings, but doesn't understand strategy concepts.
Typical mistakes: playing too many hands, not betting strong hands, calling too much, chasing draws without pot odds awareness.

**Communication style**:
- Use plain language
- Define every term the first time you use it
- Use analogies ("Think of the pot like a prize pool you're competing for")
- Focus on one concept per feedback
- Avoid: GTO, EV, fold equity, MDF, polarized ranges
- Use instead: "bet because you have a strong hand," "fold because you're probably losing"
- Praise any correct fundamental decision explicitly

**Example (beginner)**:
> You have the top pair with the best kicker. This is a strong hand right now. When the opponent checked to you, that means they showed weakness. This is the right moment to bet — you want to grow the pot when you're winning. A bet of about half the pot (around 50 chips) is perfect here. If you check, you miss chips you could have won, and you let the opponent see a free card that might beat you.

---

### Intermediate
**Profile**: Understands hand rankings, position basics, and simple strategy. Knows when to bet but may not know sizing or range concepts.
Typical mistakes: poor bet sizing, ignoring position, bluffing too much or too little, not considering opponent ranges.

**Communication style**:
- Introduce strategy concepts by name
- Explain *why* a concept applies here, not just what it is
- Reference position and board texture
- Can use: pot odds, equity (briefly explained), c-bet, semi-bluff, position
- Avoid: GTO, MDF, solver output, balanced ranges
- Connect the feedback to a broader pattern

**Example (intermediate)**:
> You have top pair top kicker in position on a dry board (no flush or straight draws). This is a classic value betting spot. When you check back here, you're leaving chips on the table and giving villain a free card. A bet of 50–66% pot achieves two goals: you build value while you're ahead, and you charge draws if any exist. On a board this dry, sizing down to 33% pot is also fine — fewer hands call anyway.

---

### Advanced
**Profile**: Understands ranges, pot odds, and basic GTO concepts. Can think about hand frequencies and balance.
Typical mistakes: range imbalances, weak spots in sizing strategy, incorrect GTO vs exploit decisions.

**Communication style**:
- Reference range vs range dynamics
- Discuss how this action interacts with the overall strategy
- Can use: EV, fold equity, polarized range, merged range, GTO, balance, blockers
- Challenge the player to think beyond individual hands
- Point out how this spot fits into a larger pattern

**Example (advanced)**:
> With TPTK in position on an A72r board, checking back has some merit as a slow-play or protection for your checking range, but it's a significant EV leak if you check your entire top pair range here. A balanced strategy uses most of your TPTK as a bet given range advantage on this texture. Villain's BB range doesn't hit A-high boards well. A 33–50% pot bet maximizes EV while building a credible betting range that includes both value and some bluffs.

---

### Pro
**Profile**: Understands GTO, can run mental equity calculations, studies solver outputs, thinks in frequencies.
Typical mistakes: over-exploitative adjustments, solver output misapplication, ignoring dynamic adjustments.

**Communication style**:
- Speak directly, technically
- Challenge assumptions: "What does your range look like here?"
- Reference solver-derived frequencies when relevant
- Ask about meta-game and exploitative adjustments
- No hand-holding — go straight to the nuance

**Example (pro)**:
> On A72r OOP vs BTN, GTO checks at high frequency with TPTK to protect your checking range. However, the correct implementation depends on your board coverage advantage. If BTN's calling range is wide (pre-flop open-calls a lot), range betting 30–40% is solver-preferred. Your TPTK is part of the value combo cluster but has high show-down value that makes it a natural candidate for the betting range rather than a slow-play vehicle.

---

## Adaptation Procedure

Before writing any output, the coaching agent must:

1. Read `memory/user_profile.md` → get `user_level`
2. Select the appropriate communication style from this skill
3. Apply a vocabulary filter:
   - Beginner: plain language only
   - Intermediate: introduce named concepts, briefly define them
   - Advanced: use full technical vocabulary
   - Pro: assume full vocabulary knowledge, add nuance
4. Control explanation length:
   - Beginner: 3–5 sentences, focus on one concept
   - Intermediate: 4–7 sentences, connect concept to context
   - Advanced: full analysis, references to range theory
   - Pro: concise but dense, no padding

---

## Motivation and Encouragement

### Beginners
After any correct decision (even partial):
> "That was a good call — you recognized you had enough equity for the price."

After a mistake:
> "This is a common spot to get wrong. Here's the simple way to remember it next time:"

### Intermediate/Advanced
Minimal praise — focus on the concept. Only highlight decisions that show real improvement.

### All Levels
After a luck loss (played correctly, lost anyway):
> "You made the right play. That result was pure variance. Keep making the same decision — over thousands of hands, it wins money."

---

## Concepts by Level

| Concept | Beginner | Intermediate | Advanced | Pro |
|---------|----------|-------------|----------|-----|
| Hand rankings | ✅ Core | ✅ Core | ✅ Core | ✅ Core |
| Position | Simple intro | Position advantage | Range impact | Equilibrium |
| Bet sizing | "Bet half pot" | Sizing by board | Sizing by range | Mixed strategies |
| Pot odds | Not introduced | Calculate and decide | EV framing | Implicit |
| Bluffing | "Bluff rarely" | When to semi-bluff | Fold equity math | Balanced ranges |
| Equity | Not introduced | "% chance of winning" | Exact calculation | Implicitly used |
| GTO | Not mentioned | Not mentioned | Referenced | Core vocabulary |
