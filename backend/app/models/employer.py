"""
Employer-side schemas. The public posting is deliberately thin (title + seniority +
years) — the real requirements live in `HiddenRequirements` and are never shown to
candidates until they're shortlisted.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.candidate import SeniorityLevel


class HiddenRequirements(BaseModel):
    """The actual JD. Stored server-side only; revealed post-match to shortlisted candidates."""

    full_description: str
    required_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    location: str | None = Field(None, description="Required if on_site is True")
    on_site: bool = False
    min_years_experience: float = 0
    other_notes: str = ""


class JobPostingCreate(BaseModel):
    """What the employer submits — this is ALL candidates ever see pre-shortlist."""

    title: str
    seniority_level: SeniorityLevel
    years_experience_required: float = Field(..., ge=0)
    company_name: str
    hidden_requirements: HiddenRequirements


class JobPostingPublic(BaseModel):
    """The public-facing view candidates browse — no hidden_requirements field at all."""

    id: str
    title: str
    seniority_level: SeniorityLevel
    years_experience_required: float
    company_name: str
    created_at: datetime


class JobPosting(JobPostingCreate):
    id: str
    created_at: datetime
