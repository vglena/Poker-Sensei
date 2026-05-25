# Skill: Poker Rules — Texas Hold'em

## Overview

This skill defines the complete ruleset for Texas Hold'em as used by the training system.
The agent must know these rules to evaluate legal actions, detect mistakes, and explain rulings.

---

## The Deck

- 52 cards: ranks 2–A, suits clubs (♣), diamonds (♦), hearts (♥), spades (♠)
- No jokers
- Ace plays high (pair of aces > pair of kings) and low (A-2-3-4-5 straight)

---

## Hand Rankings (Best to Worst)

| Rank | Name | Example |
|------|------|---------|
| 10 | Royal Flush | A♥K♥Q♥J♥T♥ |
| 9 | Straight Flush | 9♠8♠7♠6♠5♠ |
| 8 | Four of a Kind | K♥K♠K♣K♦ + any |
| 7 | Full House | Q♥Q♠Q♦ + J♥J♠ |
| 6 | Flush | A♦J♦7♦5♦2♦ |
| 5 | Straight | T♥9♣8♦7♠6♥ |
| 4 | Three of a Kind | 7♥7♠7♣ + any two |
| 3 | Two Pair | A♥A♠ + K♥K♣ + any |
| 2 | One Pair | J♦J♣ + three kickers |
| 1 | High Card | A♠Q♦9♣5♥2♠ |

**Tie-breaking**: kickers determine ties within the same rank. The highest kicker wins.

---

## Betting Rounds

Texas Hold'em has four betting rounds (streets):

### 1. Preflop
- Each player is dealt 2 hole cards (face down)
- Action starts with the player left of the big blind (Under the Gun)
- Available actions: **fold, call, raise**

### 2. Flop
- 3 community cards are dealt face up
- Action starts with the first active player left of the dealer button
- Available actions: **check, bet, fold** (if facing a bet: call, raise, fold)

### 3. Turn
- 1 additional community card is dealt face up (4 total)
- Same action order as flop
- Same available actions

### 4. River
- 1 final community card is dealt face up (5 total)
- Same action order as flop/turn
- Same available actions

---

## Legal Actions

| Action | When Legal | Description |
|--------|-----------|-------------|
| **Fold** | Always | Discard cards, forfeit pot |
| **Check** | No bet has been made this round | Pass action to next player |
| **Call** | Facing a bet or raise | Match the current bet amount |
| **Bet** | No bet has been made this round | Initiate betting |
| **Raise** | Facing a bet | Increase the bet amount |
| **All-in** | Stack ≤ required amount | Commit all remaining chips |

**Important**: You cannot check if there is a bet in front of you. You must call, raise, or fold.

---

## Betting Structure (No-Limit)

- **Minimum bet**: Equal to the big blind (preflop) or the previous bet size (postflop)
- **Minimum raise**: Must be at least double the previous bet (or the size of the previous raise)
- **Maximum bet**: All of your chips (no-limit)
- **No cap**: Players can re-raise unlimited times (in no-limit)

---

## Position

Positions in a 6-handed game (most common in training):

| Position | Abbreviation | Description |
|----------|-------------|-------------|
| Under the Gun | UTG | First to act preflop (left of BB). Tightest range. |
| Hijack | HJ | Two left of BTN |
| Cutoff | CO | One left of BTN |
| Button | BTN | Last to act postflop. Most powerful position. |
| Small Blind | SB | Posts half BB. Acts before BB preflop, first postflop. |
| Big Blind | BB | Posts full BB. Acts last preflop, first postflop. |

**Positional advantage**: Acting last (BTN) gives you more information before you decide.

---

## Pot Logic

- The pot consists of all chips bet in the current hand
- Side pots are created when a player is all-in with less than the current bet
- The player with the best hand at showdown wins the pot (or the last remaining share if multiple pots)

---

## Showdown

- Occurs when two or more players remain after the river and a bet/call occurs
- Last aggressor shows first; if checked down, player left of dealer shows first
- Best 5-card hand using any combination of 2 hole cards and 5 community cards wins
- A player may use 0, 1, or 2 hole cards (board can play if it's the best 5-card hand)

---

## Blinds

- Small Blind (SB): mandatory bet = 0.5 × Big Blind
- Big Blind (BB): mandatory bet = 1 BB
- Antes (optional): small mandatory bet from all players before the hand

---

## Important Edge Cases

- **Chopped pot**: two players have identical best hands → split the pot evenly
- **Dead money**: chips from folded players stay in the pot
- **String bets**: illegal — you must declare "raise" before adding chips
- **Acting out of turn**: illegal in live play; in software, prevent with UI constraints
