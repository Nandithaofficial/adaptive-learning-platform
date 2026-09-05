"""
test_pipeline.py — Unit tests with real assertions (not just eyeballed output).

Run with: python3 -m pytest test_pipeline.py -v
(or: python3 test_pipeline.py  — falls back to a plain assertion runner
if pytest isn't installed)
"""

import decision_agent
from validators import validate_attempt, validate_ids, ValidationError


def test_advance_on_high_score():
    report = {"latest_score": 90, "time_ratio": 1.0, "reinforcement_count": 0,
               "attempt_count": 1, "score_trend": 0, "is_rushing": False,
               "is_struggling": False, "hints_used": 0}
    decision, reason = decision_agent.decide(report)
    assert decision == "advance"
    assert reason == "mastery_achieved"


def test_reinforce_on_first_low_score():
    report = {"latest_score": 55, "time_ratio": 1.0, "reinforcement_count": 0,
               "attempt_count": 1, "score_trend": 0, "is_rushing": False,
               "is_struggling": False, "hints_used": 0}
    decision, reason = decision_agent.decide(report)
    assert decision == "reinforce"
    assert reason == "below_mastery_threshold"


def test_mentor_after_max_reinforcements():
    report = {"latest_score": 55, "time_ratio": 1.0, "reinforcement_count": 3,
               "attempt_count": 4, "score_trend": 0, "is_rushing": False,
               "is_struggling": False, "hints_used": 0}
    decision, reason = decision_agent.decide(report)
    assert decision == "mentor"
    assert reason == "reinforcement_exhausted"


def test_mentor_on_declining_trend():
    report = {"latest_score": 45, "time_ratio": 1.0, "reinforcement_count": 0,
               "attempt_count": 2, "score_trend": -15, "is_rushing": False,
               "is_struggling": False, "hints_used": 0}
    decision, reason = decision_agent.decide(report)
    assert decision == "mentor"
    assert reason == "declining_trend"


def test_reinforce_on_rushing():
    report = {"latest_score": 40, "time_ratio": 0.3, "reinforcement_count": 0,
               "attempt_count": 1, "score_trend": 0, "is_rushing": True,
               "is_struggling": False, "hints_used": 0}
    decision, reason = decision_agent.decide(report)
    assert decision == "reinforce"
    assert reason == "rushing_low_effort"


def test_validate_attempt_rejects_out_of_range_score():
    try:
        validate_attempt({"score": 150, "time_spent_sec": 100})
        assert False, "expected ValidationError"
    except ValidationError:
        pass


def test_validate_attempt_rejects_missing_score():
    try:
        validate_attempt({"time_spent_sec": 100})
        assert False, "expected ValidationError"
    except ValidationError:
        pass


def test_validate_attempt_applies_defaults():
    clean = validate_attempt({"score": 80, "time_spent_sec": 100})
    assert clean["expected_time_sec"] == 300
    assert clean["hints_used"] == 0


def test_validate_ids_rejects_empty_learner_id():
    try:
        validate_ids("", "topic1")
        assert False, "expected ValidationError"
    except ValidationError:
        pass


if __name__ == "__main__":
    # Plain runner fallback if pytest isn't installed.
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {t.__name__} -> {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
