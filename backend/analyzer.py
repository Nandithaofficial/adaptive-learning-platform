"""
analyzer.py — The Analyzer Agent.

Public entry point: analyze(learner_id, topic_id, new_attempt)

Pipeline:
  1. Load existing progress record (or create new one)
  2. Append the new attempt
  3. Extract signals from full attempt history
  4. Run rule-based decision engine -> (decision, reason_code)
  5. Generate mentor-friendly reasoning (LLM if available, else template)
  6. Update + persist progress record
  7. Log the decision for audit/history
  8. Return a structured result matching the hackathon's expected output
"""

import db
import signals as signal_engine
import decision as decision_engine
import llm_reasoning


def analyze(learner_id: str, topic_id: str, new_attempt: dict) -> dict:
    """
    new_attempt example:
    {
        "score": 58,
        "time_spent_sec": 540,
        "expected_time_sec": 300,
        "hints_used": 3
    }
    """
    progress = db.get_progress(learner_id, topic_id)
    progress["attempts"].append(new_attempt)

    extracted_signals = signal_engine.extract_signals(progress)
    decision, reason_code = decision_engine.decide(extracted_signals)
    template_reason = decision_engine.render_reason(reason_code, extracted_signals)
    reasoning = llm_reasoning.generate_reasoning(
        decision, reason_code, extracted_signals, fallback_text=template_reason
    )

    # Update progress record based on the decision
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
    db.log_decision(learner_id, topic_id, decision, reasoning)

    return {
        "learner_id": learner_id,
        "topic_id": topic_id,
        "decision": decision,
        "reason_code": reason_code,
        "reasoning": reasoning,
        "signals": extracted_signals,
        "updated_progress": progress,
    }


if __name__ == "__main__":
    db.init_db()
    print("Analyzer module loaded. Run demo.py for a full walkthrough.")
