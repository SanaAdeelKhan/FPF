"""
Matching endpoints: run a candidate against a posting, and reveal the full JD +
match explanation once shortlisted. This is the "wow moment" route — messy CV in,
hidden JD, transparent match score out.
"""

from fastapi import APIRouter, HTTPException

from app.db import memory_store
from app.models.match import MatchResult
from app.services.explainer import generate_explanation
from app.services.matching_engine import compute_match

router = APIRouter(prefix="/matching", tags=["matching"])

# Candidates scoring at or above this overall score are auto-shortlisted.
# Tune once matching quality is validated against mock data (see scripts/seed_mock_data.py).
SHORTLIST_THRESHOLD = 0.65


@router.post("/run/{candidate_id}/{posting_id}", response_model=MatchResult)
def run_match(candidate_id: str, posting_id: str):
    candidate = memory_store.get_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate.parsed_profile is None:
        raise HTTPException(status_code=400, detail="Candidate's CV has not been parsed yet")

    posting = memory_store.get_posting(posting_id)
    if posting is None:
        raise HTTPException(status_code=404, detail="Job posting not found")

    overall_score, factor_scores = compute_match(candidate, posting)
    explanation = generate_explanation(overall_score, factor_scores)
    shortlisted = overall_score >= SHORTLIST_THRESHOLD

    result = MatchResult(
        candidate_id=candidate_id,
        job_posting_id=posting_id,
        overall_score=overall_score,
        factor_scores=factor_scores,
        explanation=explanation,
        shortlisted=shortlisted,
    )
    memory_store.save_match(result)
    return result


@router.get("/reveal/{candidate_id}/{posting_id}")
def reveal_jd(candidate_id: str, posting_id: str):
    """Return the full hidden JD, but ONLY if this candidate was shortlisted."""
    match = memory_store.get_match(candidate_id, posting_id)
    if match is None:
        raise HTTPException(status_code=404, detail="No match found for this candidate/posting pair — run matching first")
    if not match.shortlisted:
        raise HTTPException(status_code=403, detail="Candidate was not shortlisted for this role")

    posting = memory_store.get_posting(posting_id)
    if posting is None:
        raise HTTPException(status_code=404, detail="Job posting not found")

    return posting.hidden_requirements
