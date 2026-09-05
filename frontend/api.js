// api.js — Thin client for the Adaptive Learning Coach backend.
// Backend must be running: cd backend && python3 app.py  (default: http://localhost:5000)

const BASE_URL = "http://localhost:5000/api";

/**
 * Submit a new attempt and get back a decision (reinforce/advance/mentor).
 * @param {string} learnerId
 * @param {string} topicId
 * @param {{score: number, time_spent_sec: number, expected_time_sec?: number, hints_used?: number}} attempt
 */
export async function analyzeAttempt(learnerId, topicId, attempt) {
  const res = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ learner_id: learnerId, topic_id: topicId, attempt }),
  });
  if (!res.ok) throw new Error(`Analyze failed: ${res.status}`);
  return res.json();
}

/** Get all progress records (across topics) for one learner. */
export async function getLearnerProgress(learnerId) {
  const res = await fetch(`${BASE_URL}/progress/${learnerId}`);
  if (!res.ok) throw new Error(`Progress fetch failed: ${res.status}`);
  return res.json();
}

/** Full decision audit log — for the mentor dashboard. */
export async function getAllDecisions() {
  const res = await fetch(`${BASE_URL}/decisions`);
  if (!res.ok) throw new Error(`Decisions fetch failed: ${res.status}`);
  return res.json();
}

/** Decision log filtered to one learner. */
export async function getLearnerDecisions(learnerId) {
  const res = await fetch(`${BASE_URL}/decisions/${learnerId}`);
  if (!res.ok) throw new Error(`Decisions fetch failed: ${res.status}`);
  return res.json();
}
