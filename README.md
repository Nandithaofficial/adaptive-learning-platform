# Adaptive Learning Coach — Team Repo

Hackathon Problem #8. Decides whether a learner should **reinforce**,
**advance**, or get a **mentor** check-in based on their attempt history.

```
adaptive-learning-coach/
├── backend/          Python: analyzer agent, decision engine, Flask API
├── frontend/         React/HTML dashboard (student + mentor views)
└── README.md         This file
```

## Quick start (everyone runs this first)

```bash
git clone https://github.com/YOUR_USERNAME/adaptive-learning-coach.git
cd adaptive-learning-coach/backend
pip install -r requirements.txt --break-system-packages   # or use a venv
python3 demo.py        # sanity check: runs 6 synthetic learner journeys
python3 app.py          # starts the API on http://localhost:5000
```

Test the API is alive: open `http://localhost:5000/api/health` in a browser
— you should see `{"status": "ok"}`.

Optional (only if you want LLM-written explanations instead of templates):
```bash
cp backend/.env.example backend/.env
# add your ANTHROPIC_API_KEY to backend/.env, then:
export ANTHROPIC_API_KEY=your_key_here
```
Without a key, the app still works fully — it uses clear template-based
explanations instead. Nobody is blocked by not having a key.

## How the pieces fit together

```
Frontend (React)  --HTTP-->  Flask API (backend/app.py)  -->  Analyzer Agent
                                                                (backend/analyzer.py)
                                                                     |
                                                          decision.py + signals.py
                                                                     |
                                                              db.py (SQLite)
```

The frontend never touches the decision logic directly — it only calls the
API endpoints below. This means backend and frontend can be built in
parallel without blocking each other, as long as everyone agrees on this
contract.

## API contract (backend/app.py)

**`POST /api/analyze`** — submit an attempt, get a decision back
```json
// request
{
  "learner_id": "L001",
  "topic_id": "fractions_multiplication",
  "attempt": {"score": 58, "time_spent_sec": 320, "expected_time_sec": 300, "hints_used": 1}
}
// response
{
  "learner_id": "L001",
  "topic_id": "fractions_multiplication",
  "decision": "reinforce",
  "reason_code": "below_mastery_threshold",
  "reasoning": "Score of 58% is below the 70% mastery threshold...",
  "signals": { ... },
  "updated_progress": { ... }
}
```

**`GET /api/progress/<learner_id>`** — all topic progress for one learner

**`GET /api/decisions`** — full decision audit log (for the mentor dashboard)

**`GET /api/decisions/<learner_id>`** — decision log for one learner

Frontend devs: use `frontend/api.js` — it already wraps all four calls
with fetch, so you can just `import { analyzeAttempt } from './api.js'`.

## Suggested task split (4 people)

| Person | Owns | Files |
|---|---|---|
| **You** | Analyzer agent + decision logic (done) | `backend/decision.py`, `signals.py`, `analyzer.py` |
| **Person 2** | API + backend integration/testing | `backend/app.py`, writing more test cases in `demo.py` |
| **Person 3** | Student-facing view (submit attempt, see result/next step) | `frontend/` — student page |
| **Person 4** | Mentor dashboard (decision log, flagged learners, reasoning) | `frontend/` — mentor page, calls `/api/decisions` |

Person 2 and 3/4 can start immediately using `backend/app.py` — they don't
need to wait for anyone, since the API is already working end-to-end.

## Git workflow (keep it simple for a hackathon)

1. **Never push directly to `main`** once more than one person is committing —
   use branches:
   ```bash
   git checkout -b feature/mentor-dashboard
   # ... make changes ...
   git add .
   git commit -m "Add mentor dashboard skeleton"
   git push -u origin feature/mentor-dashboard
   ```
   Then open a Pull Request on GitHub into `main` so others can see the diff
   before it merges. For a hackathon, self-merging your own PR after a
   quick look is fine — the point is just to avoid silently overwriting
   someone else's work.

2. **Pull before you push**, always:
   ```bash
   git pull origin main
   ```

3. **If you get a merge conflict**, don't panic — call out in your team
   chat, open the conflicting file, look for `<<<<<<<` markers, and decide
   together which version to keep.

4. Commit often, in small chunks — "added mentor endpoint" not
   "day 1 progress."

## What NOT to commit

Already handled by `.gitignore`, but worth knowing:
- `backend/learning_coach.db` — everyone generates their own local copy by running `demo.py` or `app.py`
- `backend/.env` — contains your personal API key, never commit this
- `node_modules/`, `__pycache__/` — regenerated automatically

## Current status

- [x] Decision engine (rule-based, 3 outcomes: reinforce/advance/mentor)
- [x] Signal extraction from attempt history
- [x] SQLite persistence + decision audit log
- [x] Optional LLM reasoning layer (graceful fallback if no API key)
- [x] Flask REST API wrapping the agent
- [x] Synthetic test suite (`backend/demo.py`) covering all decision paths
- [ ] Student-facing frontend view
- [ ] Mentor dashboard frontend view
- [ ] Deployment (if needed for demo day — e.g. Render/Railway for backend, Vercel/Netlify for frontend)
