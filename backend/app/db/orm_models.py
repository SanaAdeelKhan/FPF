"""
SQLAlchemy ORM models — the persistent schema replacing memory_store's in-process
dicts. Four tables:

    Company       — one row per hiring company (was implicit `company_name` string)
    JobPostingORM — one posting, belongs to a Company, has an apply_by deadline
    CandidateORM  — one candidate PROFILE, created once, reused across every
                    posting they apply to (was previously created fresh per upload)
    Application   — the join between a Candidate and a JobPosting: one row per
                    "this candidate applied to this posting". Carries the match
                    score/explanation AND the lifecycle status (pending ->
                    selected/not_selected), so the "no candidate waits forever"
                    guarantee has a concrete field to hang off: `status` flips
                    away from `pending` only when the posting's close-out runs.

Design notes:
- hidden_requirements and parsed_profile are stored as JSON columns rather than
  their own tables — they're always read/written whole, never queried by their
  internal fields, so a normalized table would add joins for no real benefit.
- `shortlisted` is computed and stored at match-time (instant, same as today),
  but candidates/employers don't see the yes/no until `status` resolves at
  the posting's deadline. Two fields, not one, is deliberate: it keeps "did they
  match" (fact) separate from "has it been revealed yet" (lifecycle).
- SQLite for local/demo (already the default in session.py); same models work
  against Postgres on Render with zero code changes, only DATABASE_URL.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def new_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ApplicationStatus(str, enum.Enum):
    pending = "pending"
    selected = "selected"
    not_selected = "not_selected"
    withdrawn = "withdrawn"


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, index=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    postings: Mapped[list["JobPostingORM"]] = relationship(back_populates="company")


class JobPostingORM(Base):
    __tablename__ = "job_postings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True)

    title: Mapped[str] = mapped_column(String)
    seniority_level: Mapped[str] = mapped_column(String)  # SeniorityLevel enum value
    years_experience_required: Mapped[float] = mapped_column(Float)

    # Full JD — never serialized into any public-facing response model.
    hidden_requirements: Mapped[dict] = mapped_column(JSON)

    apply_by: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closed: Mapped[bool] = mapped_column(Boolean, default=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    company: Mapped["Company"] = relationship(back_populates="postings")
    applications: Mapped[list["Application"]] = relationship(back_populates="posting")


class CandidateORM(Base):
    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    full_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String)
    seniority_level: Mapped[str] = mapped_column(String)
    years_experience: Mapped[float] = mapped_column(Float)
    availability: Mapped[str] = mapped_column(String)
    open_to_remote: Mapped[bool] = mapped_column(Boolean, default=True)

    cv_raw_text: Mapped[str] = mapped_column(Text)
    parsed_profile: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    applications: Mapped[list["Application"]] = relationship(back_populates="candidate")


class Application(Base):
    """One candidate's application to one posting. Created on apply, scored
    immediately, but its yes/no is withheld from both sides until the posting's
    deadline triggers close-out (see app/services/closeout.py)."""

    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), index=True)
    job_posting_id: Mapped[str] = mapped_column(ForeignKey("job_postings.id"), index=True)

    overall_score: Mapped[float] = mapped_column(Float)
    factor_scores: Mapped[list] = mapped_column(JSON)  # list[MatchFactorScore]-shaped dicts
    explanation: Mapped[str] = mapped_column(Text)
    shortlisted: Mapped[bool] = mapped_column(Boolean)  # computed fact, set at apply-time

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.pending
    )

    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    candidate: Mapped["CandidateORM"] = relationship(back_populates="applications")
    posting: Mapped["JobPostingORM"] = relationship(back_populates="applications")
