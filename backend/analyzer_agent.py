"""
analyzer_agent.py — The ANALYZER AGENT.

Role: perceive and interpret. This agent looks at a learner's raw attempt
history (scores, time spent, hints used) and produces an ANALYZED REPORT —
a clean set of signals that summarize the learner's current state.

It does NOT make any reinforce/advance/mentor decision. That responsibility
belongs entirely to decision_agent.py. This separation matters: the
Analyzer Agent can get smarter over time (more signals, better trend
detection, even an LLM-based read of qualitative patterns) without ever
touching decision logic, and vice versa.

Public entry point: analyze_learner(progress) -> report dict
"""


def analyze_learner(progress: dict) -> dict:
    """
    Takes a learner's progress record (with attempt history) and returns
    an analyzed report: the signals the Decision Agent needs to act on.
    """
    attempts = progress["attempts"]
    if not attempts:
        raise ValueError("Analyzer Agent: cannot analyze — no attempts recorded yet.")

    latest = attempts[-1]
    scores = [a["score"] for a in attempts]

    avg_score = sum(scores) / len(scores)
    score_trend = scores[-1] - scores[-2] if len(scores) > 1 else 0

    time_ratio = None
    if latest.get("expected_time_sec"):
        time_ratio = latest["time_spent_sec"] / latest["expected_time_sec"]

    # Rushing vs struggling heuristic:
    # fast + wrong = rushing/guessing, slow + wrong = genuinely struggling.
    is_rushing = (
        time_ratio is not None and time_ratio < 0.6 and latest["score"] < 70
    )
    is_struggling = (
        time_ratio is not None and time_ratio > 1.3 and latest["score"] < 70
    )

    report = {
        "learner_id": progress["learner_id"],
        "topic_id": progress["topic_id"],
        "latest_score": latest["score"],
        "avg_score": round(avg_score, 1),
        "score_trend": score_trend,        # positive = improving, negative = declining
        "time_ratio": time_ratio,          # >1 = slower than expected, <1 = faster
        "attempt_count": len(attempts),
        "hints_used": latest.get("hints_used", 0),
        "reinforcement_count": progress.get("reinforcement_count", 0),
        "is_rushing": is_rushing,
        "is_struggling": is_struggling,
    }
    return report
