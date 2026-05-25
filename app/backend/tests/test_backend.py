"""
tests/test_backend.py
---------------------
Lightweight backend tests using pytest + FastAPI TestClient.

Run with:
    cd app/backend
    pip install pytest httpx
    pytest tests/ -v

These tests cover the canonical endpoints and core analysis pipeline.
They do not test UI logic or agent strategy — only the HTTP interface.
"""

import sys
from pathlib import Path

# Ensure agent/execution and app/shared are importable from test context.
REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "agent" / "execution"))
sys.path.insert(0, str(REPO_ROOT / "app" / "shared"))
sys.path.insert(0, str(REPO_ROOT / "app" / "backend"))

from fastapi.testclient import TestClient
from main import app  # noqa: E402

client = TestClient(app)

# ---------------------------------------------------------------------------
# Fixtures — scenario endpoints
# ---------------------------------------------------------------------------

FIXTURE_NAMES = ["preflop_raise", "flop_cbet", "turn_draw", "river_bluff_catch", "value_bet_sizing"]


def test_fixture_list_returns_five():
    """GET /api/scenario/fixtures — should return exactly 5 entries."""
    response = client.get("/api/scenario/fixtures")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5


def test_fixture_list_has_required_fields():
    """Each fixture entry must have name, label, description, street, difficulty."""
    response = client.get("/api/scenario/fixtures")
    data = response.json()
    for item in data:
        assert "name" in item
        assert "label" in item
        assert "description" in item
        assert "street" in item
        assert "difficulty" in item


def test_get_known_fixture_preflop_raise():
    """GET /api/scenario/fixture/preflop_raise — must return a valid PokerScenario."""
    response = client.get("/api/scenario/fixture/preflop_raise")
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == "fixture-preflop-raise-001"
    assert data["street"] == "preflop"
    assert "As" in data["hole_cards"]
    assert "Ks" in data["hole_cards"]
    assert "raise" in data["available_actions"]


def test_get_fixture_not_found():
    """GET /api/scenario/fixture/unknown — must return 404."""
    response = client.get("/api/scenario/fixture/not_a_real_fixture")
    assert response.status_code == 404


def test_all_five_fixtures_load():
    """All 5 fixture names should load without error."""
    for name in FIXTURE_NAMES:
        response = client.get(f"/api/scenario/fixture/{name}")
        assert response.status_code == 200, f"Fixture '{name}' failed to load"
        data = response.json()
        assert "scenario_id" in data
        assert "hole_cards" in data
        assert "available_actions" in data


# ---------------------------------------------------------------------------
# Decision analysis — valid and invalid actions
# ---------------------------------------------------------------------------

def _preflop_raise_payload(action: str, bet_amount=None) -> dict:
    """Build a valid decision payload using the preflop_raise fixture."""
    scenario = client.get("/api/scenario/fixture/preflop_raise").json()
    payload = {
        "session_id": "test-session-001",
        "scenario_id": scenario["scenario_id"],
        "user_action": action,
        "bet_amount": bet_amount,
        "user_level": "beginner",
        "scenario_data": scenario,
    }
    return payload


def test_decision_analyze_valid_action_raise():
    """POST /api/decision/analyze — valid raise returns DecisionAnalysis."""
    payload = _preflop_raise_payload("raise", bet_amount=90.0)
    response = client.post("/api/decision/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "decision_id" in data
    assert "rating" in data
    assert data["rating"] in ("good", "ok", "mistake", "blunder")
    assert "rating_score" in data
    assert 1 <= data["rating_score"] <= 10
    assert "explanation" in data
    assert "recommended_drill" in data


def test_decision_analyze_returns_mistake_category():
    """POST /api/decision/analyze — response must include mistake_category field."""
    payload = _preflop_raise_payload("fold")
    response = client.post("/api/decision/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    # mistake_category may be None for good decisions but field must be present
    assert "mistake_category" in data


def test_decision_invalid_action_rejected():
    """
    POST /api/decision/analyze — illegal action returns a blunder rating
    (not a 422 or 500) so the frontend always gets displayable feedback.
    """
    payload = _preflop_raise_payload("check")  # check is not available preflop in this fixture
    response = client.post("/api/decision/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Illegal action is returned as a blunder with score 1
    assert data["rating"] == "blunder"
    assert data["rating_score"] == 1


def test_decision_missing_scenario_data():
    """POST /api/decision/analyze without scenario_data must return 422."""
    payload = {
        "session_id": "test-session-001",
        "scenario_id": "some-id",
        "user_action": "fold",
        "user_level": "beginner",
        # no scenario_data
    }
    response = client.post("/api/decision/analyze", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Session report
# ---------------------------------------------------------------------------

def test_session_report_nonexistent_returns_404():
    """GET /api/session/{id}/summary — unknown session must return 404."""
    response = client.get("/api/session/this-session-does-not-exist/summary")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def test_health_check():
    """GET /api/health must return 200 with status field."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"


# ---------------------------------------------------------------------------
# New scenario endpoint
# ---------------------------------------------------------------------------

def test_new_scenario_returns_valid_structure():
    """GET /api/scenario/new must return a valid PokerScenario."""
    response = client.get("/api/scenario/new")
    assert response.status_code == 200
    data = response.json()
    assert "scenario_id" in data
    assert "hole_cards" in data
    assert len(data["hole_cards"]) == 2
    assert "available_actions" in data
    assert len(data["available_actions"]) > 0
