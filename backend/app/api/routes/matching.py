"""
Matching endpoints. Two-step now, not one:

  1. POST /matching/apply/{posting_id} — computes the match score immediately
     (same rule-based engine as before) and stores it, but the response withholds
     the outcome. Application sits at `pending`. The applying candidate is the
     one identified by the auth token, not a URL param.
  2. GET /matching/status/{posting_id} — checks the posting's deadline (closing
     it out if passed) and returns whatever the logged-in candidate is currently
     allowed to see: a wait message if still pending, or the full result (+ JD
     reveal if selected) once resolved.

This is the backend half of "no candidate waits in silence forever" — the
guarantee is enforced by never letting `shortlisted` leak through a response
until `status` has actually resolved.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.core.deps import get_current_candidate
from app.db import store
from app.db.adapters import to_candidate_schema, to_posting_schema
from app.db.orm_models import ApplicationStatus, CandidateORM
from app.db.session import get_db
from app.models.application import ApplicationStatusView, ApplyResponse
from app.services import closeout
from app.services.explainer import generate_explanation
from app.services.matching_engine import compute_match

router = APIRouter(prefix="/matching", tags=["matching"])

# Candidates scoring at or above this overall score are auto-shortlisted.
# Tune once matching quality is validated against mock data (see scripts/seed_mock_data.py).
SHORTLIST_THRESHOLD = 0.65


@router.post("/apply/{posting_id}", response_model=ApplyResponse)
def apply_to_posting(
    posting_id: str,
    current_candidate: CandidateORM = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    if current_candidate.parsed_profile is None:
        raise HTTPException(status_code=400, detail="Your CV has not been uploaded/parsed yet")

    posting = store.get_posting(db, posting_id)
    if posting is None:
        raise HTTPException(status_code=404, detail="Job posting not found")

    # Close-out first: if the deadline already passed (or the posting was already
    # closed), we must not let a fresh application sit at "pending" forever —
    # close_if_past_deadline only resolves applications that exist *before* it
    # runs, so a late apply needs to resolve itself immediately below instead.
    posting = closeout.close_if_past_deadline(db, posting)

    existing = store.get_application(db, current_candidate.id, posting_id)
    if existing is not None:
        return ApplyResponse(
            application_id=existing.id,
            status=existing.status,
            apply_by=posting.apply_by,
            message="You've already applied to this posting.",
        )

    overall_score, factor_scores = compute_match(
        to_candidate_schema(current_candidate), to_posting_schema(posting)
    )
    explanation = generate_explanation(overall_score, factor_scores)
    shortlisted = overall_score >= SHORTLIST_THRESHOLD

    application = store.save_application(
        db,
        candidate_id=current_candidate.id,
        job_posting_id=posting_id,
        overall_score=overall_score,
        factor_scores=[factor.model_dump() for factor in factor_scores],
        explanation=explanation,
        shortlisted=shortlisted,
    )

    if posting.closed:
        # Applied after the deadline had already passed — resolve immediately
        # rather than leaving a pending row no future close-out run will touch.
        resolved_status = ApplicationStatus.selected if shortlisted else ApplicationStatus.not_selected
        application = store.resolve_application(db, application, resolved_status)
        return ApplyResponse(
            application_id=application.id,
            status=application.status,
            apply_by=posting.apply_by,
            message="This posting's deadline already passed, so your result is ready now — check status.",
        )

    return ApplyResponse(
        application_id=application.id,
        status=application.status,
        apply_by=posting.apply_by,
        message=f"Application received. You'll get a definitive yes or no by {posting.apply_by:%b %d, %Y}.",
    )


@router.get("/status/{posting_id}", response_model=ApplicationStatusView)
def get_application_status(
    posting_id: str,
    current_candidate: CandidateORM = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    application = store.get_application(db, current_candidate.id, posting_id)
    if application is None:
        raise HTTPException(status_code=404, detail="No application found for this posting")

    posting = store.get_posting(db, posting_id)
    if posting is None:
        raise HTTPException(status_code=404, detail="Job posting not found")

    posting = closeout.close_if_past_deadline(db, posting)
    application = store.get_application(db, current_candidate.id, posting_id)  # re-fetch post-closeout

    if application.status == ApplicationStatus.pending:
        return ApplicationStatusView(
            application_id=application.id,
            job_title=posting.title,
            company_name=posting.company.name,
            status=application.status,
            apply_by=posting.apply_by,
            message=f"Still pending — you'll hear back by {posting.apply_by:%b %d, %Y}.",
        )

    if application.status == ApplicationStatus.selected:
        return ApplicationStatusView(
            application_id=application.id,
            job_title=posting.title,
            company_name=posting.company.name,
            status=application.status,
            apply_by=posting.apply_by,
            overall_score=application.overall_score,
            factor_scores=application.factor_scores,
            explanation=application.explanation,
            hidden_requirements=posting.hidden_requirements,
            message="You've been selected! Full job details are below.",
        )

    # not_selected
    return ApplicationStatusView(
        application_id=application.id,
        job_title=posting.title,
        company_name=posting.company.name,
        status=application.status,
        apply_by=posting.apply_by,
        overall_score=application.overall_score,
        factor_scores=application.factor_scores,
        explanation=application.explanation,
        message="You weren't selected for this role this time. Here's how your profile compared.",
    )


@router.patch("/withdraw/{posting_id}", response_model=ApplyResponse)
def withdraw_application_route(
    posting_id: str,
    current_candidate: CandidateORM = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    application = store.get_application(db, current_candidate.id, posting_id)
    if application is None:
        raise HTTPException(status_code=404, detail="No application found for this posting")

    if application.status == ApplicationStatus.withdrawn:
        raise HTTPException(status_code=400, detail="Application already withdrawn")

    posting = store.get_posting(db, posting_id)
    application = store.withdraw_application(db, application)

    return ApplyResponse(
        application_id=application.id,
        status=application.status,
        apply_by=posting.apply_by,
        message="Your application has been withdrawn.",
    )


@router.delete("/apply/{posting_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_application_route(
    posting_id: str,
    current_candidate: CandidateORM = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    application = store.get_application(db, current_candidate.id, posting_id)
    if application is None:
        raise HTTPException(status_code=404, detail="No application found for this posting")

    store.delete_application(db, application)
