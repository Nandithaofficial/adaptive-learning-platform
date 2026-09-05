"""
coach.py — The Orchestrator.

This is the top-level pipeline that ties the three agents together. It is
NOT itself where analysis or decisions happen — it just runs them in order
and persists the result. This mirrors the flow described in the problem
statement: track progress -> analyze -> decide -> report + update records.

Pipeline:
  1. Load the learner's existing progress record (or create a new one)
  2. Append the new attempt to their history
  3. ANALYZER AGENT: turn attempt history into an analyzed signal report
  4. DECISION AGENT: turn that report into a decision + reason code
  5. REASONING AGENT: turn the reason code into mentor-friendly prose
  6. Update + persist the learner's progress record
  7. Log the decision to the audit trail
  8. Return a structured result (matches the hackathon's expected output)

Public entry point: run(learner_id, topic_id, new_attempt) -> result dict
"""

import db
import analyzer_agent
import decision_agent
import reasoning_agent
from validators import validate_attempt, validate_ids


def run(learner_id: str, topic_id: str, new_attempt: dict) -> dict:
    """
    new_attempt example:
    {
        "score": 58,
        "time_spent_sec": 540,
        "expected_time_sec": 300,
        "hints_used": 3
    }
    """
    validate_ids(learner_id, topic_id)
    clean_attempt = validate_attempt(new_attempt)

    # --- Load + update progress ---
    progress = db.get_progress(learner_id, topic_id)
    progress["attempts"].append(clean_attempt)

    # --- Stage 1: Analyzer Agent ---
    report = analyzer_agent.analyze_learner(progress)

    # --- Stage 2: Decision Agent ---
    decision, reason_code = decision_agent.decide(report)
    template_reason = decision_agent.render_reason(reason_code, report)

    # --- Stage 3: Reasoning Agent (optional LLM explanation layer) ---
    reasoning = reasoning_agent.explain(
        decision, reason_code, report, fallback_text=template_reason
    )

    # --- Update progress record based on the decision ---
    if decision == "reinforce":
        progress["reinforcement_count"] += 1
        progress["mastery_status"] = "in_progress"
    elif decision == "advance":
        progress["mastery_status"] = "mastered"
        progress["reinforcement_count"] = 0  # reset for the next topic
    elif decision == "mentor":
        progress["mastery_status"] = "stuck"

    progress["last_decision"] = decision

    db.save_progress(progress)
    db.log_decision(learner_id, topic_id, decision, reason_code, reasoning)

    return {
        "learner_id": learner_id,
        "topic_id": topic_id,
        "decision": decision,
        "reason_code": reason_code,
        "reasoning": reasoning,
        "analyzed_report": report,
        "updated_progress": progress,
    }


if __name__ == "__main__":
    db.init_db()
    print("Coach pipeline loaded. Run demo.py for a full walkthrough.")
