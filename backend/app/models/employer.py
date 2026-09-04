"""
Employer-side schemas. The public posting is deliberately thin (title + seniority +
years) — the real requirements live in `HiddenRequirements` and are never shown to
candidates until they're shortlisted AND the posting's deadline has closed it out.
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
    """What the employer submits — this is ALL candidates ever see pre-shortlist.
    company_name is deliberately NOT here: the posting company is the logged-in
    employer (from the auth token), never a client-supplied string."""

    title: str
    seniority_level: SeniorityLevel
    years_experience_required: float = Field(..., ge=0)
    apply_by: datetime = Field(..., description="Deadline — every applicant gets a definitive yes/no by this time")
    hidden_requirements: HiddenRequirements


class JobPostingPublic(BaseModel):
    """The public-facing view candidates browse — no hidden_requirements field at all.
    apply_by IS shown — candidates should know upfront when they'll hear back."""

    id: str
    title: str
    seniority_level: SeniorityLevel
    years_experience_required: float
    company_name: str
    apply_by: datetime
    closed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class JobPosting(JobPostingCreate):
    """Full internal shape (includes hidden_requirements) — used by the matching
    engine, never returned directly from any API route. company_name added back
    here since the matching engine schema still expects it."""

    id: str
    company_name: str
    closed: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
