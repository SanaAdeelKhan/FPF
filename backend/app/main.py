"""
FPF backend entrypoint. Run locally with:
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, candidates, employers, matching
from app.core.config import settings
from app.db import orm_models  # noqa: F401 — import registers models on Base.metadata
from app.db.session import Base, engine

app = FastAPI(
    title="FPF — Finding Perfect Fit",
    description="A fair-hiring platform that hides the JD until the match is proven.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(employers.router)
app.include_router(candidates.router)
app.include_router(matching.router)


@app.on_event("startup")
def on_startup():
    # create_all is fine for a hackathon timeline — no migration history needed yet.
    # If this becomes a real production app, swap to Alembic migrations instead.
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}
