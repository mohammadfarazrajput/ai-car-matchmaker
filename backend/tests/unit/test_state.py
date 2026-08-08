"""Session state, slot provenance, and resume tokens."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.agent import state as st
from app.models.schemas import Session


@pytest.fixture(autouse=True)
def _clean_tokens() -> None:
    st.reset_tokens_for_tests()


# --- slots -------------------------------------------------------------------


def test_new_session_is_missing_all_four_core_slots() -> None:
    s = st.new_state("s1")
    assert st.missing_slots(s) == ["intent", "category", "budget_max", "target_date"]
    assert not st.interview_complete(s)


def test_filling_all_four_completes_the_interview() -> None:
    s = st.new_state("s1")
    for slot, value in [("intent", "rent"), ("category", "suv"),
                        ("budget_max", 900), ("target_date", "2026-09-03")]:
        st.record_slot(s, slot, value, "web")
    assert st.interview_complete(s)
    assert st.missing_slots(s) == []


def test_slot_records_its_channel_of_origin() -> None:
    """FR-022 — lets the agent say 'you mentioned on the phone that…'."""
    s = st.new_state("s1", channel="web")
    st.record_slot(s, "intent", "buy", "phone")
    assert s["slot_origin"]["intent"]["channel"] == "phone"
    datetime.fromisoformat(s["slot_origin"]["intent"]["at"])  # parses


# --- revision (FR-004) -------------------------------------------------------


def test_revising_a_slot_clears_stale_results() -> None:
    """Recommendations must never outlive the inputs that produced them."""
    s = st.new_state("s1")
    s["ranked"] = [{"listing_id": "l-1", "rank": 1, "score": 0.9,
                    "breakdown": {"budget": 1.0, "category": 1.0,
                                  "features": 1.0, "date": 1.0},
                    "reasoning": "…"}]
    s["selected_car_id"] = "l-1"
    s["phase"] = "RANKED"

    st.record_slot(s, "budget_max", 120_000, "web")

    assert s["ranked"] == []
    assert s["selected_car_id"] is None
    assert s["phase"] == "RESEARCHING"


def test_setting_a_slot_to_the_same_value_keeps_results() -> None:
    """Re-affirming an answer is not a revision — re-ranking would be wasteful."""
    s = st.new_state("s1")
    st.record_slot(s, "budget_max", 65_000, "web")
    s["ranked"] = [{"listing_id": "l-1", "rank": 1, "score": 0.9,
                    "breakdown": {"budget": 1.0, "category": 1.0,
                                  "features": 1.0, "date": 1.0},
                    "reasoning": "…"}]
    st.record_slot(s, "budget_max", 65_000, "web")
    assert len(s["ranked"]) == 1


def test_confirmed_booking_is_immutable() -> None:
    s = st.new_state("s1")
    s["phase"] = "CONFIRMED"
    with pytest.raises(ValueError, match="confirmed"):
        st.record_slot(s, "budget_max", 1, "web")


# --- conversion --------------------------------------------------------------


def test_round_trips_through_the_validated_session_model() -> None:
    s = st.new_state("s1", channel="phone")
    for slot, value in [("intent", "rent"), ("category", "suv"),
                        ("budget_max", 900), ("target_date", "2026-09-03")]:
        st.record_slot(s, slot, value, "phone")

    session = st.to_session(s)
    assert isinstance(session, Session)
    assert session.budget is not None and session.budget.max == 900
    assert session.target_date is not None and session.target_date.isoformat() == "2026-09-03"
    assert session.entry_channel == "phone"

    back = st.from_session(session)
    assert back["intent"] == "rent"
    assert back["budget_max"] == 900
    assert back["target_date"] == "2026-09-03"


def test_client_snapshot_hides_internals() -> None:
    s = st.new_state("s1")
    st.record_slot(s, "intent", "buy", "web")
    snap = st.client_snapshot(s)
    assert "slot_origin" not in snap
    assert "messages" not in snap
    assert snap["missing"] == ["category", "budget_max", "target_date"]


# --- checkpointer ------------------------------------------------------------


def test_checkpointer_is_a_singleton() -> None:
    assert st.build_checkpointer() is st.build_checkpointer()


def test_thread_config_keys_on_session_id() -> None:
    assert st.thread_config("abc")["configurable"]["thread_id"] == "abc"


# --- resume tokens (FR-023) --------------------------------------------------


def test_token_round_trips() -> None:
    token = st.issue_resume_token("s1")
    assert st.redeem_resume_token(token.code) == "s1"


def test_token_is_single_use() -> None:
    token = st.issue_resume_token("s1")
    st.redeem_resume_token(token.code)
    with pytest.raises(st.ResumeTokenError) as e:
        st.redeem_resume_token(token.code)
    assert e.value.reason == "used"


def test_expired_token_is_rejected_with_a_reason() -> None:
    token = st.issue_resume_token("s1")
    token.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    with pytest.raises(st.ResumeTokenError) as e:
        st.redeem_resume_token(token.code)
    assert e.value.reason == "expired"


def test_unknown_token_is_rejected_with_a_reason() -> None:
    """A reason, not a bare 404 — FR-023 requires an explanation and a way forward."""
    with pytest.raises(st.ResumeTokenError) as e:
        st.redeem_resume_token("ZZZZZ")
    assert e.value.reason == "unknown"


def test_code_avoids_visually_ambiguous_characters() -> None:
    """Codes get read aloud on the phone handoff."""
    codes = "".join(st.issue_resume_token(f"s{i}").code for i in range(60))
    assert not set(codes) & set("IO01")


def test_codes_are_unpredictable() -> None:
    codes = {st.issue_resume_token(f"s{i}").code for i in range(50)}
    assert len(codes) == 50
