"""
Real persistence layer, replacing app/db/memory_store.py.

Kept function-shaped the same way memory_store was (save_x / get_x) so route
files change as little as possible. The one real difference callers must adapt
to: every function here takes a `db: Session` first argument (FastAPI injects
it via `Depends(get_db)`), since SQLAlchemy sessions aren't global like the old
in-memory dicts were.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.orm_models import (
    Application,
    ApplicationStatus,
    CandidateORM,
    Company,
    JobPostingORM,
)


# --- companies ---

def get_or_create_company(db: Session, name: str) -> Company:
    company = db.scalar(select(Company).where(Company.name == name))
    if company is None:
        company = Company(name=name)
        db.add(company)
        db.commit()
        db.refresh(company)
    return company


# --- candidates ---
# Candidate is now created ONCE and reused across postings — look up by email
# first so a returning candidate doesn't get a duplicate profile/CV re-parse.

def get_candidate_by_email(db: Session, email: str) -> CandidateORM | None:
    return db.scalar(select(CandidateORM).where(CandidateORM.email == email))


def save_candidate(db: Session, **fields) -> CandidateORM:
    candidate = CandidateORM(**fields)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def get_candidate(db: Session, candidate_id: str) -> CandidateORM | None:
    return db.get(CandidateORM, candidate_id)


def update_candidate_parsed_profile(db: Session, candidate: CandidateORM, parsed_profile: dict) -> CandidateORM:
    candidate.parsed_profile = parsed_profile
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


# --- postings ---

def save_posting(db: Session, company: Company, **fields) -> JobPostingORM:
    posting = JobPostingORM(company_id=company.id, **fields)
    db.add(posting)
    db.commit()
    db.refresh(posting)
    return posting


def get_posting(db: Session, posting_id: str) -> JobPostingORM | None:
    return db.get(JobPostingORM, posting_id)


def list_open_postings(db: Session) -> list[JobPostingORM]:
    return list(db.scalars(select(JobPostingORM).where(JobPostingORM.closed == False)))  # noqa: E712


def list_postings_past_deadline_unclosed(db: Session) -> list[JobPostingORM]:
    now = datetime.now(timezone.utc)
    return list(
        db.scalars(
            select(JobPostingORM).where(
                JobPostingORM.closed == False,  # noqa: E712
                JobPostingORM.apply_by <= now,
            )
        )
    )


# --- applications ---

def get_application(db: Session, candidate_id: str, posting_id: str) -> Application | None:
    return db.scalar(
        select(Application).where(
            Application.candidate_id == candidate_id,
            Application.job_posting_id == posting_id,
        )
    )


def save_application(db: Session, **fields) -> Application:
    application = Application(**fields)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def list_applications_for_posting(db: Session, posting_id: str) -> list[Application]:
    return list(db.scalars(select(Application).where(Application.job_posting_id == posting_id)))


def list_applications_for_candidate(db: Session, candidate_id: str) -> list[Application]:
    return list(db.scalars(select(Application).where(Application.candidate_id == candidate_id)))


def resolve_application(db: Session, application: Application, status: ApplicationStatus) -> Application:
    application.status = status
    application.resolved_at = datetime.now(timezone.utc)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def withdraw_application(db: Session, application: Application) -> Application:
    application.status = ApplicationStatus.withdrawn
    application.resolved_at = datetime.now(timezone.utc)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def delete_application(db: Session, application: Application) -> None:
    db.delete(application)
    db.commit()
