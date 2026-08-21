"""
Candidate-facing endpoints: upload a CV (guided fields + raw text), parse it
synchronously via cv_parser, and store the structured profile.
"""

from fastapi import APIRouter, HTTPException

from app.db import memory_store
from app.models.candidate import Candidate, CandidateCreate
from app.services.cv_parser import parse_cv

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("", response_model=Candidate)
def upload_candidate(candidate_in: CandidateCreate):
    """Store candidate, parse CV synchronously, save the structured profile."""
    candidate = memory_store.save_candidate(candidate_in)
    candidate.parsed_profile = parse_cv(candidate_in.cv_raw_text)
    memory_store.update_candidate(candidate)
    return candidate


@router.get("/{candidate_id}", response_model=Candidate)
def get_candidate(candidate_id: str):
    candidate = memory_store.get_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
