"""
Matching endpoints: run a candidate against a posting (or all postings), and reveal
the full JD + match explanation once shortlisted. This is the "wow moment" route —
messy CV in, hidden JD, transparent match score out.
"""

from fastapi import APIRouter

from app.models.match import MatchResult

router = APIRouter(prefix="/matching", tags=["matching"])


@router.post("/run/{candidate_id}/{posting_id}", response_model=MatchResult)
def run_match(candidate_id: str, posting_id: str):
    """
    Orchestrates: fetch candidate + posting -> matching_engine.compute_match ->
    explainer.generate_explanation -> persist MatchResult -> return it.
    """
    raise NotImplementedError("matching.run_match: wire up the full pipeline")


@router.get("/reveal/{candidate_id}/{posting_id}")
def reveal_jd(candidate_id: str, posting_id: str):
    """Return the full hidden JD, but ONLY if this candidate was shortlisted."""
    raise NotImplementedError("matching.reveal_jd: check shortlisted=True before returning hidden_requirements")
