"""
decision_logger.py
------------------
Deterministic module for logging user decisions to structured records.

Version 1: File-based logging using JSON Lines format (.jsonl).
One file per session. Each line is a complete decision record.

Designed to be replaced with a database later without changing the interface.

Public API:
    DecisionLogger              — Main logging class
    create_decision_record(...) — Build a DecisionRecord from scenario + action
    get_logger(session_id)      — Get or create the active logger
"""

import json
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path


# ---------------------------------------------------------------------------
# Default storage path
# ---------------------------------------------------------------------------

DEFAULT_LOG_DIR = Path(__file__).parent.parent / "memory" / "logs"


# ---------------------------------------------------------------------------
# Decision record
# ---------------------------------------------------------------------------

@dataclass
class DecisionRecord:
    """A single logged user decision."""
    decision_id: str
    session_id: str
    scenario_id: str
    timestamp: str                  # ISO 8601 UTC
    street: str                     # preflop | flop | turn | river
    hole_cards: List[str]
    community_cards: List[str]
    pot_size: float
    user_action: str                # fold | check | call | bet | raise
    bet_amount: Optional[float]     # Amount if user bet or raised
    hero_position: str
    villain_position: str
    rating: str                     # good | ok | mistake | blunder
    rating_score: int               # 1–10
    difficulty: str
    user_level: str
    analysis_id: Optional[str] = None           # Link to the full analysis record
    mistake_category: Optional[str] = None      # e.g. passive_play, hand_selection
    explanation_summary: Optional[str] = None   # First 200 chars of explanation
    recommended_action: Optional[str] = None    # What the agent recommended instead

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecisionRecord":
        return cls(**data)


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------

def create_decision_record(
    session_id: str,
    scenario: Dict[str, Any],
    user_action: str,
    bet_amount: Optional[float],
    rating: str,
    rating_score: int,
    user_level: str,
    analysis_id: Optional[str] = None,
    mistake_category: Optional[str] = None,
    explanation_summary: Optional[str] = None,
    recommended_action: Optional[str] = None,
) -> DecisionRecord:
    """
    Build a DecisionRecord from a scenario dict and user action.

    Args:
        session_id:   The current training session ID
        scenario:     The scenario dict (from scenario_engine.to_dict())
        user_action:  The action the user took (fold/check/call/bet/raise)
        bet_amount:   The amount if user bet or raised (None otherwise)
        rating:       Decision quality: "good" | "ok" | "mistake" | "blunder"
        rating_score: Integer 1–10
        user_level:   User's current level
        analysis_id:  Optional link to the analysis record

    Returns:
        DecisionRecord ready to be logged
    """
    if rating not in ("good", "ok", "mistake", "blunder"):
        raise ValueError(f"Invalid rating: '{rating}'")
    if not (1 <= rating_score <= 10):
        raise ValueError(f"rating_score must be 1–10, got {rating_score}")

    return DecisionRecord(
        decision_id=str(uuid.uuid4()),
        session_id=session_id,
        scenario_id=scenario.get("scenario_id", "unknown"),
        timestamp=datetime.now(timezone.utc).isoformat(),
        street=scenario.get("street", "unknown"),
        hole_cards=scenario.get("hole_cards", []),
        community_cards=scenario.get("community_cards", []),
        pot_size=float(scenario.get("pot_size", 0)),
        user_action=user_action,
        bet_amount=bet_amount,
        hero_position=scenario.get("hero_position", "unknown"),
        villain_position=scenario.get("villain_position", "unknown"),
        rating=rating,
        rating_score=rating_score,
        difficulty=scenario.get("difficulty", "beginner"),
        user_level=user_level,
        analysis_id=analysis_id,
        mistake_category=mistake_category,
        explanation_summary=explanation_summary,
        recommended_action=recommended_action,
    )


# ---------------------------------------------------------------------------
# Logger class
# ---------------------------------------------------------------------------

class DecisionLogger:
    """
    File-based decision logger.

    Writes JSON lines to a per-session log file.
    One record per line for easy streaming and appending.
    """

    def __init__(
        self,
        log_dir: Path = DEFAULT_LOG_DIR,
        session_id: Optional[str] = None,
    ) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id or str(uuid.uuid4())
        self.log_file = self.log_dir / f"decisions_{self.session_id}.jsonl"

    def log(self, record: DecisionRecord) -> None:
        """Append a decision record to the session log file."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(record.to_json() + "\n")

    def read_session(self) -> List[DecisionRecord]:
        """Read and parse all records for this session."""
        if not self.log_file.exists():
            return []
        records: List[DecisionRecord] = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        records.append(DecisionRecord.from_dict(data))
                    except (json.JSONDecodeError, TypeError):
                        continue  # Skip malformed lines
        return records

    def session_summary(self) -> Dict[str, Any]:
        """Generate a summary of this session's performance."""
        records = self.read_session()
        if not records:
            return {"session_id": self.session_id, "total_decisions": 0}

        total = len(records)
        ratings = [r.rating for r in records]
        scores = [r.rating_score for r in records]

        streets: Dict[str, int] = {}
        for r in records:
            streets[r.street] = streets.get(r.street, 0) + 1

        good_or_ok = ratings.count("good") + ratings.count("ok")

        return {
            "session_id": self.session_id,
            "total_decisions": total,
            "average_score": round(sum(scores) / total, 2),
            "good": ratings.count("good"),
            "ok": ratings.count("ok"),
            "mistakes": ratings.count("mistake"),
            "blunders": ratings.count("blunder"),
            "accuracy_pct": round(good_or_ok / total * 100, 1),
            "streets_played": streets,
            "first_decision": records[0].timestamp if records else None,
            "last_decision": records[-1].timestamp if records else None,
        }

    @classmethod
    def list_sessions(cls, log_dir: Path = DEFAULT_LOG_DIR) -> List[str]:
        """Return all session IDs that have recorded decisions."""
        log_dir = Path(log_dir)
        if not log_dir.exists():
            return []
        return [
            f.stem.replace("decisions_", "")
            for f in log_dir.glob("decisions_*.jsonl")
        ]

    @classmethod
    def get_all_decisions(cls, log_dir: Path = DEFAULT_LOG_DIR) -> List[DecisionRecord]:
        """Load all decisions from all sessions (use carefully — can be large)."""
        all_records: List[DecisionRecord] = []
        for session_id in cls.list_sessions(log_dir):
            logger = cls(log_dir=log_dir, session_id=session_id)
            all_records.extend(logger.read_session())
        return all_records


# ---------------------------------------------------------------------------
# Module-level singleton (optional convenience)
# ---------------------------------------------------------------------------

_active_logger: Optional[DecisionLogger] = None


def get_logger(session_id: Optional[str] = None) -> DecisionLogger:
    """
    Get or create the active module-level logger.
    Useful when a single logger is reused across multiple function calls.
    """
    global _active_logger
    if _active_logger is None or (session_id and _active_logger.session_id != session_id):
        _active_logger = DecisionLogger(session_id=session_id)
    return _active_logger


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        logger = DecisionLogger(log_dir=Path(tmpdir), session_id="test-001")

        record = create_decision_record(
            session_id="test-001",
            scenario={
                "scenario_id": "s001",
                "street": "flop",
                "hole_cards": ["Ah", "Kd"],
                "community_cards": ["Ac", "7h", "2c"],
                "pot_size": 100,
                "hero_position": "BTN",
                "villain_position": "BB",
                "difficulty": "beginner",
            },
            user_action="check",
            bet_amount=None,
            rating="mistake",
            rating_score=4,
            user_level="beginner",
        )

        logger.log(record)

        summary = logger.session_summary()
        print("Session summary:")
        print(json.dumps(summary, indent=2))
