# FPF — Finding Perfect Fit

A fair-hiring platform that removes the incentive to game the system.

## The problem

Hiring today is a mutual gaming exercise. Employers post detailed job descriptions;
candidates reverse-engineer CVs stuffed with keywords to beat ATS filters; if they
land an interview, some use AI to fake real-time answers. Nobody is being evaluated
on what they can actually do.

## The idea: hide the target

- Employers post only a **job title, seniority level, and years of experience
  required** — no detailed JD upfront.
- Candidates upload a focused 2-page CV describing what they're genuinely best at,
  not tailored to a JD they can't see.
- An AI privately matches each CV against the employer's actual (hidden)
  requirements — skills, location (for on-site roles), seniority fit, availability,
  and other real-world factors.
- Only shortlisted candidates receive the full JD.
- Every shortlist comes with a transparent match explanation, e.g.:
  > "87% match: strong skill overlap, location compatible, seniority aligned."

## Roadmap: fair-interview layer

AI-faked interview answers are part of the same underlying problem. Planned next
step: live, unscripted video interviews with AI-generated real-time follow-up
questions — designed to be much harder to fake convincingly than typed or scripted
answers. Not built for this submission; see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Stack

- **Backend:** FastAPI (Python), Claude API for CV parsing / matching / explanation
- **Frontend:** React + Vite + TypeScript
- **Deployment:** backend on Render, frontend on Netlify (separate deploys, one repo)

## Repo structure

```
backend/    FastAPI app — API routes, matching engine, CV parser, explainer
frontend/   React + Vite app — employer posting, candidate upload, shortlist reveal
docs/       Architecture notes and demo assets
scripts/    Mock data seeding for demo/testing
```

## Local setup

See [docs/SETUP.md](docs/SETUP.md) for full instructions. Quick start:

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

Backend runs at `http://localhost:8000` (docs at `/docs`), frontend at
`http://localhost:5173`.

## Demo

_Video link and live deployment URL go here once recorded/deployed._

## Team

Built for the AI Builders Hackathon (Devpost), Aug–Sep 2026.
