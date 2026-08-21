"""
Candidate-facing endpoints: upload a CV (guided fields + raw text), trigger parsing.
"""

from fastapi import APIRouter

from app.models.candidate import Candidate, CandidateCreate

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("", response_model=Candidate)
def upload_candidate(candidate: CandidateCreate):
    """Store candidate, parse CV via cv_parser.parse_cv, save the structured profile."""
    raise NotImplementedError("candidates.upload_candidate: persist + parse")


@router.get("/{candidate_id}", response_model=Candidate)
def get_candidate(candidate_id: str):
    raise NotImplementedError("candidates.get_candidate: fetch by id")
