"""
Employer-facing endpoints: post a job (title + seniority + years, publicly),
store the hidden requirements server-side, and return only the public view.
"""

from fastapi import APIRouter, HTTPException

from app.db import memory_store
from app.models.employer import JobPostingCreate, JobPostingPublic

router = APIRouter(prefix="/employers", tags=["employers"])


@router.post("/postings", response_model=JobPostingPublic)
def create_posting(posting_in: JobPostingCreate):
    """Create a job posting. hidden_requirements is stored but never echoed back here —
    the response_model itself excludes that field, so it can't leak even by accident."""
    posting = memory_store.save_posting(posting_in)
    return posting


@router.get("/postings/{posting_id}/shortlist")
def get_shortlist(posting_id: str):
    """Return shortlisted candidates + their match explanations for this posting."""
    posting = memory_store.get_posting(posting_id)
    if posting is None:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return memory_store.get_shortlist_for_posting(posting_id)
