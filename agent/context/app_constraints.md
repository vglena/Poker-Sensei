# App Constraints

## Core Purpose

This application is an **educational poker training tool**.

It teaches strategy, decision-making, and poker thinking through simulated scenarios and AI coaching.

---

## What This App Is

- A poker learning and practice environment
- A strategy coaching system
- A tool for improving decision-making under uncertainty
- A single-player simulation with an AI opponent

---

## What This App Is NOT

These constraints are non-negotiable and must be respected by all agents, all code, and all future features.

### ❌ Not a Gambling App
- No real money is ever involved
- No chips have monetary value
- No deposits, withdrawals, or wallets
- No connection to any payment system
- No wagering of any kind

### ❌ Not a Multiplayer App
- Users do not play against other users
- No user-to-user communication
- No leaderboards that expose other users' personal data
- No real-time matchmaking

### ❌ Not a Real Poker Client
- Cannot connect to real poker sites
- Cannot play real poker games
- Cannot be used to gain unfair advantage in real games
- Does not simulate live poker with real opponents

### ❌ Not an Addiction Risk Tool
- No dark patterns that encourage excessive play
- Session limits are encouraged, not bypassed
- Breaks are recommended after extended sessions
- No rewards designed to create compulsive behavior

---

## Regulatory Compliance Notes

Because this is educational-only:
- No gambling license is required (verify with local jurisdiction)
- No age verification is required for educational tools (verify with local jurisdiction)
- No financial regulation applies to virtual training chips

These notes are informational. Legal review is required before deployment in any specific jurisdiction.

---

## Data Privacy

The coaching system stores:
- User preferences (level, goals, style)
- Decision history (hands played, ratings, mistakes)
- Session summaries

**No sensitive personal data is required.**  
Users may use the app anonymously.

In v1: data is stored locally in files.  
In future versions: if a database is added, standard data protection practices apply (encryption at rest, minimal data collection, deletion on request).

---

## Agent Behavior Constraints

All agents must:
- Refuse any request to simulate real-money gambling
- Refuse any request to connect to external poker rooms
- Never provide advice for cheating or gaining unfair advantage in real games
- Never use manipulative language to encourage excessive training sessions

---

## Acknowledgment

This file must be reviewed when adding any new feature.
Any feature that could violate these constraints must be rejected or redesigned.
