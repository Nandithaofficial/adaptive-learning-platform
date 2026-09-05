"""
decision_agent.py — The DECISION AGENT.

Role: act on the analyzed report. This agent takes the signals produced
by analyzer_agent.py and decides one of three learning-path outcomes:
'reinforce', 'advance', or 'mentor', along with a reason code.

This is deliberately deterministic (rule-based), not an LLM call:
  - fast and free to run
  - fully testable/debuggable — you can assert exact outputs
  - reliable even if an LLM/network call fails during a live demo
  - auditable, which matters for certification/education contexts where
    a decision may need to be justified to a learner or regulator

Public entry point: decide(report, config=CONFIG) -> (decision, reason_code)
"""

CONFIG = {
    "mastery_threshold": 70,             # score % to be considered "mastered"
    "max_time_ratio_for_advance": 1.3,   # allow some slack over expected time
    "max_reinforcements": 3,             # after this many reinforce rounds, escalate to mentor
    "hint_flag_threshold": 3,            # hints used that signal conceptual gaps
    "decline_attempt_min": 2,            # need at least this many attempts to detect a trend
}


def decide(report: dict, config: dict = CONFIG) -> tuple[str, str]:
    """
    Returns (decision, reason_code) where decision is one of:
    'advance', 'reinforce', 'mentor'
    """

    # 1. Clear mastery -> advance
    if (
        report["latest_score"] >= config["mastery_threshold"]
        and (report["time_ratio"] is None or report["time_ratio"] <= config["max_time_ratio_for_advance"])
    ):
        return "advance", "mastery_achieved"

    # 2. Too many reinforcement rounds without success -> mentor
    if report["reinforcement_count"] >= config["max_reinforcements"]:
        return "mentor", "reinforcement_exhausted"

    # 3. Declining performance across attempts -> mentor (reinforcement isn't working)
    if (
        report["attempt_count"] >= config["decline_attempt_min"]
        and report["score_trend"] < 0
    ):
        return "mentor", "declining_trend"

    # 4. Struggling badly (slow + wrong) on a later attempt -> mentor
    if report["is_struggling"] and report["attempt_count"] >= config["decline_attempt_min"]:
        return "mentor", "persistent_struggle"

    # 5. Rushing/guessing -> reinforce, flagged for an engagement nudge not just content
    if report["is_rushing"]:
        return "reinforce", "rushing_low_effort"

    # 6. Heavy hint usage + low score -> reinforce (conceptual gap)
    if report["hints_used"] >= config["hint_flag_threshold"] and report["latest_score"] < config["mastery_threshold"]:
        return "reinforce", "conceptual_gap"

    # 7. Default: below mastery threshold, no red flags yet -> reinforce
    return "reinforce", "below_mastery_threshold"


# Human-readable templates for each reason code — used as the default
# explanation, and as a guaranteed fallback if the reasoning agent
# (LLM layer) is unavailable.
REASON_TEMPLATES = {
    "mastery_achieved": "Score of {latest_score}% meets the mastery threshold and was completed in reasonable time. Ready to advance.",
    "reinforcement_exhausted": "Learner has completed {reinforcement_count} reinforcement rounds on this topic without reaching mastery. Needs human mentor support.",
    "declining_trend": "Score dropped from the previous attempt (trend: {score_trend}), suggesting increasing difficulty or disengagement rather than a one-off slip.",
    "persistent_struggle": "Learner is spending significantly more time than expected and still scoring below mastery ({latest_score}%), indicating a genuine conceptual block.",
    "rushing_low_effort": "Latest attempt was completed much faster than expected with a low score ({latest_score}%), suggesting guessing rather than engagement.",
    "conceptual_gap": "High hint usage ({hints_used}) combined with a below-mastery score ({latest_score}%) points to a specific conceptual gap that reinforcement should target.",
    "below_mastery_threshold": "Score of {latest_score}% is below the {mastery_threshold}% mastery threshold. Reinforcement is recommended before retrying.",
}


def render_reason(reason_code: str, report: dict, config: dict = CONFIG) -> str:
    template = REASON_TEMPLATES[reason_code]
    context = {**config, **report}
    return template.format(**context)
