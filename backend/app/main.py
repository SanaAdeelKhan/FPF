"""
FPF backend entrypoint. Run locally with:
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import candidates, employers, matching
from app.core.config import settings

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

app.include_router(employers.router)
app.include_router(candidates.router)
app.include_router(matching.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}
