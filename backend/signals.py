"""
signals.py — Turns raw attempt history into decision-ready features.

This is the "sensing" layer of the agent: it doesn't decide anything,
it just summarizes the noisy raw data (scores, time, hints) into a clean
signal dict the decision engine can reason over.
"""


def extract_signals(progress: dict) -> dict:
    attempts = progress["attempts"]
    if not attempts:
        raise ValueError("Cannot extract signals: no attempts recorded yet.")

    latest = attempts[-1]
    scores = [a["score"] for a in attempts]

    avg_score = sum(scores) / len(scores)
    score_trend = scores[-1] - scores[-2] if len(scores) > 1 else 0

    time_ratio = None
    if latest.get("expected_time_sec"):
        time_ratio = latest["time_spent_sec"] / latest["expected_time_sec"]

    # crude "rushing vs struggling" heuristic:
    # fast + wrong = rushing/guessing, slow + wrong = genuinely struggling
    is_rushing = (
        time_ratio is not None
        and time_ratio < 0.6
        and latest["score"] < 70
    )
    is_struggling = (
        time_ratio is not None
        and time_ratio > 1.3
        and latest["score"] < 70
    )

    return {
        "latest_score": latest["score"],
        "avg_score": round(avg_score, 1),
        "score_trend": score_trend,          # positive = improving, negative = declining
        "time_ratio": time_ratio,            # >1 = slower than expected, <1 = faster
        "attempt_count": len(attempts),
        "hints_used": latest.get("hints_used", 0),
        "reinforcement_count": progress.get("reinforcement_count", 0),
        "is_rushing": is_rushing,
        "is_struggling": is_struggling,
    }
