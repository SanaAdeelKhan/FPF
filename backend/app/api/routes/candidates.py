"""
Candidate-facing endpoints. Candidate is now a REUSABLE profile: uploading with
an email that already exists returns/updates that same profile instead of
creating a duplicate — this is what lets one CV parse serve every application,
instead of re-uploading per job.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_candidate
from app.db import store
from app.db.orm_models import CandidateORM
from app.db.session import get_db
from app.models.application import CandidateApplicationSummary
from app.models.candidate import Candidate, CandidateCreate
from app.services.cv_parser import parse_cv

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("", response_model=Candidate)
def upload_candidate(candidate_in: CandidateCreate, db: Session = Depends(get_db)):
    """Create the candidate profile on first upload, or return the existing one
    (re-parsing the CV) if this email has applied before."""
    existing = store.get_candidate_by_email(db, candidate_in.email)
    if existing is not None:
        parsed = parse_cv(candidate_in.cv_raw_text)
        existing.full_name = candidate_in.full_name
        existing.location = candidate_in.location
        existing.seniority_level = candidate_in.seniority_level.value
        existing.years_experience = candidate_in.years_experience
        existing.availability = candidate_in.availability.value
        existing.open_to_remote = candidate_in.open_to_remote
        existing.cv_raw_text = candidate_in.cv_raw_text
        candidate = store.update_candidate_parsed_profile(db, existing, parsed.model_dump())
        return candidate

    candidate = store.save_candidate(
        db,
        full_name=candidate_in.full_name,
        email=candidate_in.email,
        location=candidate_in.location,
        seniority_level=candidate_in.seniority_level.value,
        years_experience=candidate_in.years_experience,
        availability=candidate_in.availability.value,
        open_to_remote=candidate_in.open_to_remote,
        cv_raw_text=candidate_in.cv_raw_text,
    )
    parsed = parse_cv(candidate_in.cv_raw_text)
    candidate = store.update_candidate_parsed_profile(db, candidate, parsed.model_dump())
    return candidate


@router.get("/me/applications", response_model=list[CandidateApplicationSummary])
def list_my_applications(
    current_candidate: CandidateORM = Depends(get_current_candidate),
):
    """All applications the logged-in candidate has made, across every posting —
    powers the 'my applications' dashboard (already-applied check, edit/delete
    entry points, statuses at a glance)."""
    return [
        CandidateApplicationSummary(
            application_id=application.id,
            job_posting_id=application.job_posting_id,
            job_title=application.posting.title,
            company_name=application.posting.company.name,
            status=application.status,
            apply_by=application.posting.apply_by,
            applied_at=application.applied_at,
        )
        for application in current_candidate.applications
    ]


@router.get("/{candidate_id}", response_model=Candidate)
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    candidate = store.get_candidate(db, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
