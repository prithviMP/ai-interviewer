# AI Interview Taker MVP (Phase 1)

This project is a text-based AI Interview Taker app MVP with a FastAPI backend and a React (Vite) frontend featuring custom-coded Aceternity UI components.

## Project Structure

- `backend/`: FastAPI server with in-memory session store.
- `frontend/`: React + Vite web application styled with Tailwind CSS & Framer Motion.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

---

### Running the Backend (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the development server:
   ```bash
   python3 -m uvicorn main:app --reload --port 8000
   ```
   The backend will be running at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

### Running the Frontend (React + Vite)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be running at [http://localhost:5173](http://localhost:5173).
