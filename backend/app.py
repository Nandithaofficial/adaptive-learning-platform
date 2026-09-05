"""
app.py — REST API for the Adaptive Learning Coach analyzer agent.

Run with: python3 app.py
Server starts on http://localhost:5000

Endpoints:
  POST /api/analyze          -> submit a new attempt, get a decision back
  GET  /api/progress/<id>    -> get all progress records for a learner
  GET  /api/decisions        -> full decision audit log (for mentor dashboard)
  GET  /api/decisions/<id>   -> decision log filtered to one learner
  GET  /api/health           -> simple health check
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

import db
from analyzer import analyze

app = Flask(__name__)
CORS(app)  # allow the frontend (running on a different port) to call this API

db.init_db()


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    Expected JSON body:
    {
        "learner_id": "L001",
        "topic_id": "fractions_multiplication",
        "attempt": {
            "score": 58,
            "time_spent_sec": 320,
            "expected_time_sec": 300,
            "hints_used": 1
        }
    }
    """
    body = request.get_json(force=True, silent=True)
    if not body:
        return jsonify({"error": "Missing or invalid JSON body"}), 400

    required = ["learner_id", "topic_id", "attempt"]
    missing = [f for f in required if f not in body]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    attempt = body["attempt"]
    if "score" not in attempt or "time_spent_sec" not in attempt:
        return jsonify({"error": "attempt must include at least 'score' and 'time_spent_sec'"}), 400

    attempt.setdefault("expected_time_sec", 300)
    attempt.setdefault("hints_used", 0)

    try:
        result = analyze(body["learner_id"], body["topic_id"], attempt)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/progress/<learner_id>", methods=["GET"])
def api_progress(learner_id):
    """Returns every topic's progress record for a given learner."""
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT data FROM progress WHERE learner_id = ?", (learner_id,)
    ).fetchall()
    conn.close()
    import json
    records = [json.loads(r["data"]) for r in rows]
    return jsonify(records), 200


@app.route("/api/decisions", methods=["GET"])
def api_decisions_all():
    return jsonify(db.get_decision_history()), 200


@app.route("/api/decisions/<learner_id>", methods=["GET"])
def api_decisions_for_learner(learner_id):
    return jsonify(db.get_decision_history(learner_id)), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
