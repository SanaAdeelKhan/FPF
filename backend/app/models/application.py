"""
Application-facing schemas — what candidates and employers actually see about
an application's lifecycle. Deliberately separate from the ORM row: candidates
should NEVER see `shortlisted` (the internal fact) directly, only `status`
(what's actually been revealed), so the field name distinction from
orm_models.py carries through here too.
"""

from datetime import datetime

from pydantic import BaseModel

from app.db.orm_models import ApplicationStatus
from app.models.employer import HiddenRequirements
from app.models.match import MatchFactorScore


class ApplyResponse(BaseModel):
    """Returned immediately on apply — deliberately withholds the outcome."""

    application_id: str
    status: ApplicationStatus  # always "pending" at this point
    apply_by: datetime
    message: str


class ApplicationStatusView(BaseModel):
    """What a candidate sees when checking on one application. Shape changes by status:
    - pending: no score/explanation shown, just a wait message
    - selected: full explanation + factor breakdown + the previously-hidden JD
    - not_selected: explanation + factor breakdown (so they understand the gap),
      framed respectfully — no hidden_requirements
    """

    application_id: str
    job_title: str
    company_name: str
    status: ApplicationStatus
    apply_by: datetime
    overall_score: float | None = None
    factor_scores: list[MatchFactorScore] | None = None
    explanation: str | None = None
    hidden_requirements: HiddenRequirements | None = None
    message: str


class EmployerApplicantView(BaseModel):
    """One row in the employer's per-posting applicant list."""

    application_id: str
    candidate_id: str
    candidate_name: str
    status: ApplicationStatus
    overall_score: float
    applied_at: datetime


class CandidateApplicationSummary(BaseModel):
    """One row in a candidate's 'my applications' dashboard — lighter than
    ApplicationStatusView, just enough to list + link into the full status page."""

    application_id: str
    job_posting_id: str
    job_title: str
    company_name: str
    status: ApplicationStatus
    apply_by: datetime
    applied_at: datetime
