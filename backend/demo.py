"""
demo.py — Synthetic test harness for the Analyzer Agent.

Runs five learner journeys that should each clearly land on a different
decision path, so you can verify the agent behaves correctly before
plugging it into a real UI or live data:

  1. L001 - Fast, high scorer               -> advance
  2. L002 - Low score, first honest attempt -> reinforce
  3. L003 - Repeated reinforcement, still failing -> mentor
  4. L004 - Declining scores across attempts -> mentor
  5. L005 - Heavy hints + borderline score   -> reinforce
  6. L006 - Rushing / guessing fast          -> reinforce (rushing)
"""

import json
import db
from analyzer import analyze


def run_case(title, learner_id, topic_id, attempts):
    print(f"\n{'=' * 70}\n{title}  (learner={learner_id}, topic={topic_id})\n{'=' * 70}")
    result = None
    for i, attempt in enumerate(attempts, 1):
        result = analyze(learner_id, topic_id, attempt)
        print(f"\n-- Attempt {i}: {attempt}")
        print(f"   Decision : {result['decision'].upper()}  (reason_code: {result['reason_code']})")
        print(f"   Reasoning: {result['reasoning']}")
    print(f"\n   Final progress record:")
    print(f"   {json.dumps(result['updated_progress'], indent=6)}")
    return result


def main():
    db.reset_db()

    # 1. Fast, high scorer -> advance
    run_case(
        "CASE 1: Strong performer",
        "L001", "fractions_multiplication",
        [{"score": 92, "time_spent_sec": 260, "expected_time_sec": 300, "hints_used": 0}],
    )

    # 2. Low score, first honest attempt -> reinforce
    run_case(
        "CASE 2: First attempt, below mastery",
        "L002", "fractions_multiplication",
        [{"score": 58, "time_spent_sec": 320, "expected_time_sec": 300, "hints_used": 1}],
    )

    # 3. Repeated reinforcement, still failing -> mentor
    run_case(
        "CASE 3: Reinforcement exhausted",
        "L003", "algebra_basics",
        [
            {"score": 50, "time_spent_sec": 400, "expected_time_sec": 300, "hints_used": 2},
            {"score": 52, "time_spent_sec": 410, "expected_time_sec": 300, "hints_used": 2},
            {"score": 55, "time_spent_sec": 420, "expected_time_sec": 300, "hints_used": 3},
            {"score": 53, "time_spent_sec": 430, "expected_time_sec": 300, "hints_used": 3},
        ],
    )

    # 4. Declining scores -> mentor
    run_case(
        "CASE 4: Declining trend",
        "L004", "geometry_angles",
        [
            {"score": 75, "time_spent_sec": 300, "expected_time_sec": 300, "hints_used": 0},
            {"score": 60, "time_spent_sec": 350, "expected_time_sec": 300, "hints_used": 1},
            {"score": 45, "time_spent_sec": 400, "expected_time_sec": 300, "hints_used": 2},
        ],
    )

    # 5. Heavy hints + borderline score -> reinforce
    run_case(
        "CASE 5: Conceptual gap (heavy hints)",
        "L005", "fractions_multiplication",
        [{"score": 62, "time_spent_sec": 310, "expected_time_sec": 300, "hints_used": 4}],
    )

    # 6. Rushing / guessing -> reinforce (rushing flavor)
    run_case(
        "CASE 6: Rushing through content",
        "L006", "fractions_multiplication",
        [{"score": 40, "time_spent_sec": 90, "expected_time_sec": 300, "hints_used": 0}],
    )

    print(f"\n{'=' * 70}\nFull decision log (audit trail):\n{'=' * 70}")
    for row in db.get_decision_history():
        print(f"  [{row['timestamp']}] {row['learner_id']} / {row['topic_id']} -> {row['decision']}")


if __name__ == "__main__":
    main()
