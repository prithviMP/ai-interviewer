# AI Interview Taker — Gemini-Powered MCQ Assessment

A web app where users configure a skill assessment and take a 5-question MCQ quiz. Questions are generated dynamically by **Google Gemini**, answers are scored instantly, and personalized AI feedback is provided at the end.

## Project Structure

- `backend/` — FastAPI server with Gemini integration, in-memory sessions, and server-side cache
- `frontend/` — React (Vite) + Tailwind CSS, simple `useState` in `App.jsx`

---

## Prerequisites

- Python 3.8+
- Node.js 18+
- Google Gemini API key ([Google AI Studio](https://aistudio.google.com/apikey))

---

## Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
python3 -m uvicorn main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | — | Required for question generation |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `QUESTION_COUNT` | `5` | Questions per assessment |
| `CACHE_TTL_SECONDS` | `3600` | Server cache TTL |

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

---

## Features

- Email/password sign-up and sign-in (JWT)
- Dashboard with sidebar: Home, New Test, Previous Tests, Reports
- Test history persisted in SQLite per user
- Gemini-generated MCQ assessments

## API Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/auth/signup` | POST | — | Create account (name, email, password) |
| `/auth/login` | POST | — | Sign in |
| `/auth/me` | GET | Yes | Current user |
| `/health` | GET | — | Health check + Gemini config status |
| `/assessments/generate` | POST | Yes | Generate MCQs via Gemini |
| `/assessments/{id}/answer` | POST | Yes | Submit MCQ answer |
| `/assessments/{id}/results` | GET | Yes | Full results breakdown |
| `/assessments/{id}/feedback` | POST | Yes | AI feedback via Gemini |
| `/history` | GET/POST | Yes | List / save completed tests |
| `/history/{id}` | GET | Yes | Single test detail |
| `/reports` | GET | Yes | Aggregate stats |
