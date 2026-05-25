# Directive: generate_session_report

## Purpose

At the end of a training session, produce a structured `SessionReport` that summarizes the user's performance, identifies recurring patterns, and recommends their next drill.

This directive is executed by `app/backend/services/agent_bridge.py → get_session_summary()`.
The output schema is `app/shared/schemas.py → SessionReport`.

---

## Inputs

| Field | Type | Source |
|-------|------|--------|
| `session_id` | `str` | Passed in from the API request |
| `records` | `list[DecisionRecord]` | Loaded from `agent/memory/logs/decisions_{session_id}.jsonl` |
| `user_level` | `str` | From the most recent `DecisionRecord.user_level` in the session |
| `session_duration` | `int \| None` | Seconds between first and last record timestamp (optional) |

Each `DecisionRecord` contains:
- `street` — preflop / flop / turn / river
- `user_action` — fold / check / call / bet / raise
- `rating` — good / ok / mistake / blunder
- `rating_score` — 1–10
- `mistake_category` — see [poker_strategy.md → Mistake Categories](../skills/poker_strategy.md)
- `explanation_summary` — first 200 chars of the full coaching explanation
- `recommended_action` — what the agent suggested as the correct play

---

## Output: SessionReport

```python
SessionReport(
    session_id: str,
    total_decisions: int,
    average_score: float,              # mean of rating_score across all records
    accuracy_pct: float,               # pct of decisions rated 'good' or 'ok'
    strongest_decision: dict | None,   # record with the highest rating_score
    weakest_decision: dict | None,     # record with the lowest rating_score
    recurring_mistake: str | None,     # most frequent mistake_category (if any)
    recommended_drill: str | None,     # mapped from recurring_mistake
    progress_note: str,                # short human-readable summary
    streets_played: dict[str, int],    # count per street e.g. {"preflop": 3, "flop": 2}
)
```

---

## Algorithm

### Step 1 — Load records

Load all `DecisionRecord` entries from the session log file.
If the file does not exist or is empty, return `None`.

### Step 2 — Compute statistics

```
total_decisions = len(records)
average_score   = mean(r.rating_score for r in records)
accuracy_pct    = (count(r.rating in ['good', 'ok']) / total_decisions) × 100
streets_played  = Counter(r.street for r in records)
```

### Step 3 — Identify strongest and weakest decisions

```
strongest = max(records, key=lambda r: r.rating_score)
weakest   = min(records, key=lambda r: r.rating_score)
```

Return as dicts with keys: `decision_id`, `street`, `user_action`, `rating`, `rating_score`, `hole_cards`.

### Step 4 — Find recurring mistake

```
mistake_counts = Counter(
    r.mistake_category for r in records
    if r.mistake_category and r.mistake_category != 'general_mistake'
)
recurring_mistake = most_common(mistake_counts) if any else None
```

### Step 5 — Map to recommended drill

Use this lookup table:

| `recurring_mistake` | `recommended_drill` |
|---------------------|---------------------|
| `passive_play` | "Practice 3-betting and c-betting: find 5 spots where you should bet but checked. Force yourself to bet." |
| `missed_value` | "Value bet sizing drill: on your next 10 hands with top pair+, commit to betting 50-75% pot on every street." |
| `hand_selection` | "Review preflop ranges: study BTN, CO, and UTG open ranges. Fold anything outside your range." |
| `over_bluff` | "Bluff discipline drill: for the next session, only bluff when you can clearly articulate villain's folding range." |
| `calling_station` | "Fold equity drill: on every bet you face, write down why villain would bluff here before calling." |
| `sizing_error` | "Bet sizing drill: practice 3 sizes (33%, 66%, pot) and understand when each applies." |
| `general_mistake` or `None` | "Fundamentals review: spend 15 minutes reading the poker strategy skill on position and bet sizing." |

### Step 6 — Generate progress note

Use this template, adapted by user level:

**beginner / intermediate:**
> "You made {total_decisions} decisions with an average score of {avg:.1f}/10 ({accuracy:.0f}% good or ok).
> {strength_note} {recurring_note}"

- `strength_note`: "Your best play was {strongest.street} — well done." if score ≥ 8, else "Keep working on your fundamentals."
- `recurring_note`: "Watch out for {recurring_mistake_label}." if recurring, else "No clear pattern — keep it up."

**advanced / pro:**
> "Session: {total_decisions} decisions, {avg:.1f}/10 avg, {accuracy:.0f}% correct.
> {recurring_note} Next: {recommended_drill_short}."

---

## Error Handling

| Case | Action |
|------|--------|
| Session not found | Return `None` |
| Session has 0 records | Return `None` |
| Session has 1 record | Return report with `strongest == weakest`, `recurring_mistake = None` |
| Log file is malformed | Log the error to stderr, return partial report with available records |

---

## Constraints

- The session report is a **summary only**. It does not re-analyze individual decisions.
- It reads from the log, not from live state. If a decision was not logged, it will not appear.
- This directive is **read-only**: it must not modify or delete any log records.
- The `progress_note` must be encouraging even when performance is poor. Never shame the user.

---

## Related

- Schema: [app/shared/schemas.py → SessionReport](../../app/shared/schemas.py)
- Implementation: [app/backend/services/agent_bridge.py → get_session_summary()](../../app/backend/services/agent_bridge.py)
- Logger: [agent/execution/decision_logger.py](../execution/decision_logger.py)
- Mistake categories: [agent/skills/poker_strategy.md → Mistake Categories](../skills/poker_strategy.md)
