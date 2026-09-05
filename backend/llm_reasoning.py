"""
llm_reasoning.py — Optional layer that turns the rule engine's terse
reason code into a warmer, mentor/learner-friendly explanation.

IMPORTANT: The LLM never changes the decision itself — it only explains
a decision that has already been made deterministically by decision.py.
This keeps the system reliable: if the API key is missing or the call
fails, we fall back to the template-based reason from decision.py and
the agent keeps working end-to-end.
"""

import os

USE_LLM = bool(os.environ.get("ANTHROPIC_API_KEY"))

if USE_LLM:
    import anthropic
    _client = anthropic.Anthropic()


def generate_reasoning(decision: str, reason_code: str, signals: dict, fallback_text: str) -> str:
    if not USE_LLM:
        return fallback_text

    prompt = f"""You are an adaptive learning coach writing a short note for a human mentor.

Decision made by the system: {decision}
Reason code: {reason_code}
Learner signals: {signals}

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
        # Never let an LLM/network hiccup break the agent during a demo.
        return f"{fallback_text} [LLM reasoning unavailable: {e}]"
