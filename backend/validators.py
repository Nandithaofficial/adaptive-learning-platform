"""
validators.py — Input validation for incoming attempt data.

Keeps bad data (negative scores, missing fields, wrong types) from ever
reaching the Analyzer or Decision Agents, where it could crash the
pipeline or silently produce a nonsensical decision.
"""


class ValidationError(Exception):
    pass


def validate_attempt(attempt: dict) -> dict:
    """
    Validates and normalizes a raw attempt dict. Raises ValidationError
    with a clear message if something is wrong. Returns a cleaned copy
    with defaults applied.
    """
    if not isinstance(attempt, dict):
        raise ValidationError("attempt must be a JSON object")

    if "score" not in attempt:
        raise ValidationError("attempt.score is required")
    if "time_spent_sec" not in attempt:
        raise ValidationError("attempt.time_spent_sec is required")

    score = attempt["score"]
    if not isinstance(score, (int, float)):
        raise ValidationError("attempt.score must be a number")
    if not (0 <= score <= 100):
        raise ValidationError("attempt.score must be between 0 and 100")

    time_spent = attempt["time_spent_sec"]
    if not isinstance(time_spent, (int, float)) or time_spent < 0:
        raise ValidationError("attempt.time_spent_sec must be a non-negative number")

    expected_time = attempt.get("expected_time_sec", 300)
    if not isinstance(expected_time, (int, float)) or expected_time <= 0:
        raise ValidationError("attempt.expected_time_sec must be a positive number")

    hints_used = attempt.get("hints_used", 0)
    if not isinstance(hints_used, (int, float)) or hints_used < 0:
        raise ValidationError("attempt.hints_used must be a non-negative number")

    return {
        "score": score,
        "time_spent_sec": time_spent,
        "expected_time_sec": expected_time,
        "hints_used": hints_used,
    }


def validate_ids(learner_id, topic_id):
    if not learner_id or not isinstance(learner_id, str):
        raise ValidationError("learner_id is required and must be a non-empty string")
    if not topic_id or not isinstance(topic_id, str):
        raise ValidationError("topic_id is required and must be a non-empty string")
