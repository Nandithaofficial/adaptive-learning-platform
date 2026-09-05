"""
reasoning_agent.py — The REASONING AGENT (optional LLM layer).

Role: translate. This agent does NOT decide anything and does NOT analyze
anything — it takes a decision the Decision Agent already made and rewrites
the terse reason code into a warmer, mentor-friendly explanation.

If ANTHROPIC_API_KEY is not set, or the API call fails for any reason, this
falls back to the deterministic template text from decision_agent.py. This
keeps the whole pipeline reliable end-to-end even with no network access —
important for a live demo.
"""

import os

USE_LLM = bool(os.environ.get("ANTHROPIC_API_KEY"))

if USE_LLM:
    import anthropic
    _client = anthropic.Anthropic()


def explain(decision: str, reason_code: str, report: dict, fallback_text: str) -> str:
    if not USE_LLM:
        return fallback_text

    prompt = f"""You are an adaptive learning coach writing a short note for a human mentor.

Decision made by the system: {decision}
Reason code: {reason_code}
Learner signals: {report}

Write 1-2 plain-language sentences explaining WHY this decision makes sense,
for a mentor who has 5 seconds to read it. Be specific about the numbers.
Do not suggest a different decision. Do not add a greeting or sign-off."""

    try:
        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        ).strip()
        return text if text else fallback_text
    except Exception as e:
        # Never let an LLM/network hiccup break the pipeline during a demo.
        return f"{fallback_text} [LLM reasoning unavailable: {e}]"
