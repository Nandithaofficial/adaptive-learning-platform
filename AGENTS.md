# AGENTS.md — Assistant instructions for this repo

Purpose: give AI coding agents the minimal, high-value facts they need to be
productive without repeating the README. Link to docs for detail.

- **Quick commands:** See the project README for full details: [README.md](README.md)
  - `cd backend && pip install -r requirements.txt` — install deps
  - `python demo.py` — run synthetic journeys (sanity checks)
  - `python app.py` — start the Flask API on http://localhost:5000

- **Deterministic decision logic (do not change):** The core decision is
  implemented in `backend/decision.py`. Agents MUST NOT alter decisions made
  by that module. If you add explanatory text, keep it separate (see LLM layer).

- **Optional LLM layer:** `backend/llm_reasoning.py` uses an Anthropic key
  when `ANTHROPIC_API_KEY` is present. The app falls back to template text if
  the key is missing or the call fails. Never make system behavior depend on
  having an LLM key available.

- **Files of interest:**
  - `backend/app.py` — Flask API and endpoint contract ([app.py](backend/app.py))
  - `backend/decision.py` — deterministic rule engine ([decision.py](backend/decision.py))
  - `backend/analyzer.py` — orchestration agent that prepares signals
  - `backend/signals.py` — signal extraction logic
  - `backend/demo.py` — test harness for synthetic learners
  - `backend/llm_reasoning.py` — optional LLM explanation layer

- **Data & secrets:**
  - Local DB: `backend/learning_coach.db` (ignored by `.gitignore`) — do not commit
  - Personal keys: `backend/.env` — never commit. Use `ANTHROPIC_API_KEY` env var.

- **Conventions & workflow:**
  - Use feature branches; don't push directly to `main` when collaborating.
  - Tests / sanity checks: prefer `python demo.py` and API healthcheck at
    `GET /api/health`.

- **How agents should help:**
  - Keep changes minimal and focused (hackathon-style sprint).
  - When proposing changes to decision logic, include unit tests in `demo.py`.
  - For UX/frontend tasks, rely on the API contract in [README.md](README.md).

- **Suggested next customizations:**
  1. `/.github/copilot-instructions.md` — short contributor-facing agent hints (CI, tests)
  2. `skills/llm-reasoning.prompt.md` — canonical prompt for `llm_reasoning.py` usage
  3. small GitHub Action to run `python demo.py` on PRs

If you'd like, I can create or update `/.github/copilot-instructions.md` next.
