# Local setup

## Prerequisites

- Python 3.11+
- Node.js 20+
- An Anthropic API key (for CV parsing / matching / explanation generation)

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: set ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

Verify it's running: `curl http://localhost:8000/health` should return
`{"status": "ok", ...}`. Interactive API docs at `http://localhost:8000/docs`.

## Frontend

```bash
cd frontend
npm install
cp .env.example .env
# edit .env if backend isn't on localhost:8000
npm run dev
```

Open `http://localhost:5173`.

## Seeding mock data (for demo/testing)

```bash
cd backend
source .venv/bin/activate
python ../scripts/seed_mock_data.py
```

## Deployment

- **Backend:** Render (Python web service). Set `ANTHROPIC_API_KEY`,
  `DATABASE_URL`, and `CORS_ORIGINS` (your Netlify URL) as environment variables
  in the Render dashboard. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Frontend:** Netlify. Build command: `npm run build`. Publish directory:
  `dist`. Set `VITE_API_BASE_URL` to your Render backend URL as a Netlify
  environment variable.
