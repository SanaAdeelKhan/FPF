"""
Employer-facing endpoints: post a job (title + seniority + years only, publicly),
store the hidden requirements server-side, never return them to unauthenticated
candidate-facing calls.
"""

from fastapi import APIRouter

from app.models.employer import JobPostingCreate, JobPostingPublic

router = APIRouter(prefix="/employers", tags=["employers"])


@router.post("/postings", response_model=JobPostingPublic)
def create_posting(posting: JobPostingCreate):
    """Create a job posting. hidden_requirements is stored but never echoed back here."""
    raise NotImplementedError("employers.create_posting: persist posting, return public view only")


@router.get("/postings/{posting_id}/shortlist")
def get_shortlist(posting_id: str):
    """Return shortlisted candidates + their match explanations for this posting."""
    raise NotImplementedError("employers.get_shortlist: query matches where shortlisted=True")
