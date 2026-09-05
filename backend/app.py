"""
app.py — REST API for the Adaptive Learning Coach.

Run with: python3 app.py
Server starts on http://localhost:5000

Endpoints:
  POST /api/analyze          -> submit a new attempt, get a decision back
  GET  /api/progress/<id>    -> all progress records for a learner
  GET  /api/decisions        -> full decision audit log (mentor dashboard)
  GET  /api/decisions/<id>   -> decision log filtered to one learner
  GET  /api/health           -> simple health check
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

import db
import coach
from validators import ValidationError

app = Flask(__name__)
CORS(app)  # allow the frontend (different port) to call this API

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

    try:
        result = coach.run(body["learner_id"], body["topic_id"], body["attempt"])
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/progress/<learner_id>", methods=["GET"])
def api_progress(learner_id):
    """Returns every topic's progress record for a given learner."""
    return jsonify(db.get_all_progress_for_learner(learner_id)), 200


@app.route("/api/decisions", methods=["GET"])
def api_decisions_all():
    return jsonify(db.get_decision_history()), 200


@app.route("/api/decisions/<learner_id>", methods=["GET"])
def api_decisions_for_learner(learner_id):
    return jsonify(db.get_decision_history(learner_id)), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
