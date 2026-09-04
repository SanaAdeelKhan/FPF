"""
Employer-facing endpoints: post a job (title + seniority + years + apply_by,
publicly), store the hidden requirements server-side, and return only the
public view. Also: list applicants for a posting (employer dashboard),
triggering deadline close-out on read so statuses are always current.

All mutating/ownership-sensitive routes now require a logged-in employer
(Company row resolved from the auth token) instead of trusting a client-
supplied company_name or an open posting_id.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_employer
from app.db import store
from app.db.orm_models import Company
from app.db.session import get_db
from app.models.application import EmployerApplicantView
from app.models.employer import JobPostingCreate, JobPostingPublic
from app.services import closeout

router = APIRouter(prefix="/employers", tags=["employers"])


@router.post("/postings", response_model=JobPostingPublic)
def create_posting(
    posting_in: JobPostingCreate,
    current_employer: Company = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """Create a job posting under the logged-in employer's company. hidden_requirements
    is stored but never echoed back here — the response_model itself excludes that
    field, so it can't leak even by accident."""
    posting = store.save_posting(
        db,
        current_employer,
        title=posting_in.title,
        seniority_level=posting_in.seniority_level.value,
        years_experience_required=posting_in.years_experience_required,
        apply_by=posting_in.apply_by,
        hidden_requirements=posting_in.hidden_requirements.model_dump(),
    )
    return JobPostingPublic(
        id=posting.id,
        title=posting.title,
        seniority_level=posting.seniority_level,
        years_experience_required=posting.years_experience_required,
        company_name=current_employer.name,
        apply_by=posting.apply_by,
        closed=posting.closed,
        created_at=posting.created_at,
    )


@router.get("/postings", response_model=list[JobPostingPublic])
def list_postings(db: Session = Depends(get_db)):
    """Public browse list for candidates — open postings only, no hidden_requirements.
    No auth required: this is the public job board."""
    postings = store.list_open_postings(db)
    result = []
    for posting in postings:
        posting = closeout.close_if_past_deadline(db, posting)
        if posting.closed:
            continue  # don't show closed postings in the open browse list
        result.append(
            JobPostingPublic(
                id=posting.id,
                title=posting.title,
                seniority_level=posting.seniority_level,
                years_experience_required=posting.years_experience_required,
                company_name=posting.company.name,
                apply_by=posting.apply_by,
                closed=posting.closed,
                created_at=posting.created_at,
            )
        )
    return result


@router.get("/me/postings", response_model=list[JobPostingPublic])
def list_my_postings(
    current_employer: Company = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """All postings belonging to the logged-in employer — for the employer dashboard's
    'my postings' list, open or closed."""
    result = []
    for posting in current_employer.postings:
        posting = closeout.close_if_past_deadline(db, posting)
        result.append(
            JobPostingPublic(
                id=posting.id,
                title=posting.title,
                seniority_level=posting.seniority_level,
                years_experience_required=posting.years_experience_required,
                company_name=current_employer.name,
                apply_by=posting.apply_by,
                closed=posting.closed,
                created_at=posting.created_at,
            )
        )
    return result


@router.get("/postings/{posting_id}/applicants", response_model=list[EmployerApplicantView])
def list_applicants(
    posting_id: str,
    current_employer: Company = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """Every applicant for this posting with their current status. Ownership check:
    only the employer who owns this posting can see its applicants. Checks the
    deadline first, so a posting past apply_by always shows resolved statuses,
    not stale 'pending' rows."""
    posting = store.get_posting(db, posting_id)
    if posting is None:
        raise HTTPException(status_code=404, detail="Job posting not found")
    if posting.company_id != current_employer.id:
        raise HTTPException(status_code=403, detail="This posting doesn't belong to your account")

    posting = closeout.close_if_past_deadline(db, posting)
    applications = store.list_applications_for_posting(db, posting_id)

    return [
        EmployerApplicantView(
            application_id=application.id,
            candidate_id=application.candidate_id,
            candidate_name=application.candidate.full_name,
            status=application.status,
            overall_score=application.overall_score,
            applied_at=application.applied_at,
        )
        for application in applications
    ]
