"""
Candidate-side schemas. A candidate uploads a focused 2-page CV; we parse it into
this structured shape before it ever gets scored against a hidden job posting.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SeniorityLevel(str, Enum):
    fresh_grad = "fresh_grad"
    mid = "mid"
    senior = "senior"


class AvailabilityType(str, Enum):
    immediate = "immediate"
    two_weeks = "two_weeks"
    one_month = "one_month"
    flexible = "flexible"


class CandidateCreate(BaseModel):
    """What the candidate submits on upload — raw CV text plus a few guided fields."""

    full_name: str
    email: str
    location: str = Field(..., description="City, country — used for on-site role matching")
    seniority_level: SeniorityLevel
    years_experience: float = Field(..., ge=0)
    availability: AvailabilityType
    open_to_remote: bool = True
    cv_raw_text: str = Field(..., description="Extracted text from the uploaded 2-page CV")


class ParsedCVProfile(BaseModel):
    """Structured output of the CV parser service — what the matching engine scores against."""

    skills: list[str] = Field(default_factory=list)
    years_experience_inferred: float | None = None
    key_strengths: list[str] = Field(default_factory=list, description="What they're genuinely best at, in their own words")
    past_roles: list[str] = Field(default_factory=list)
    summary: str = ""


class Candidate(CandidateCreate):
    id: str
    parsed_profile: ParsedCVProfile | None = None
    created_at: datetime
