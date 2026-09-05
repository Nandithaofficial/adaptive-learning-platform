"""
demo.py — Synthetic test harness for the full Coach pipeline
(Analyzer Agent -> Decision Agent -> Reasoning Agent).

Runs six learner journeys that should each clearly land on a different
decision path:

  1. L001 - Fast, high scorer                     -> advance
  2. L002 - Low score, first honest attempt        -> reinforce
  3. L003 - Repeated struggle across attempts      -> mentor
  4. L004 - Declining scores across attempts       -> mentor
  5. L005 - Heavy hints + borderline score         -> reinforce
  6. L006 - Rushing / guessing fast                -> reinforce (rushing)
"""

import json
import db
import coach


def run_case(title, learner_id, topic_id, attempts):
    print(f"\n{'=' * 70}\n{title}  (learner={learner_id}, topic={topic_id})\n{'=' * 70}")
    result = None
    for i, attempt in enumerate(attempts, 1):
        result = coach.run(learner_id, topic_id, attempt)
        print(f"\n-- Attempt {i}: {attempt}")
        print(f"   Decision : {result['decision'].upper()}  (reason_code: {result['reason_code']})")
        print(f"   Reasoning: {result['reasoning']}")
    print(f"\n   Final progress record:")
    print(f"   {json.dumps(result['updated_progress'], indent=6)}")
    return result


def main():
    db.reset_db()

    run_case(
        "CASE 1: Strong performer",
        "L001", "fractions_multiplication",
        [{"score": 92, "time_spent_sec": 260, "expected_time_sec": 300, "hints_used": 0}],
    )

    run_case(
        "CASE 2: First attempt, below mastery",
        "L002", "fractions_multiplication",
        [{"score": 58, "time_spent_sec": 320, "expected_time_sec": 300, "hints_used": 1}],
    )

    run_case(
        "CASE 3: Persistent struggle -> mentor",
        "L003", "algebra_basics",
        [
            {"score": 50, "time_spent_sec": 400, "expected_time_sec": 300, "hints_used": 2},
            {"score": 52, "time_spent_sec": 410, "expected_time_sec": 300, "hints_used": 2},
            {"score": 55, "time_spent_sec": 420, "expected_time_sec": 300, "hints_used": 3},
            {"score": 53, "time_spent_sec": 430, "expected_time_sec": 300, "hints_used": 3},
        ],
    )

    run_case(
        "CASE 4: Declining trend -> mentor",
        "L004", "geometry_angles",
        [
            {"score": 75, "time_spent_sec": 300, "expected_time_sec": 300, "hints_used": 0},
            {"score": 60, "time_spent_sec": 350, "expected_time_sec": 300, "hints_used": 1},
            {"score": 45, "time_spent_sec": 400, "expected_time_sec": 300, "hints_used": 2},
        ],
    )

    run_case(
        "CASE 5: Conceptual gap (heavy hints)",
        "L005", "fractions_multiplication",
        [{"score": 62, "time_spent_sec": 310, "expected_time_sec": 300, "hints_used": 4}],
    )

    run_case(
        "CASE 6: Rushing through content",
        "L006", "fractions_multiplication",
        [{"score": 40, "time_spent_sec": 90, "expected_time_sec": 300, "hints_used": 0}],
    )

    print(f"\n{'=' * 70}\nFull decision log (audit trail):\n{'=' * 70}")
    for row in db.get_decision_history():
        print(f"  [{row['timestamp']}] {row['learner_id']} / {row['topic_id']} -> {row['decision']} ({row['reason_code']})")


if __name__ == "__main__":
    main()
