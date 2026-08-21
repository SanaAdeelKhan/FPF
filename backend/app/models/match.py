"""
Match result schemas — the output of scoring a candidate against a job posting's
hidden requirements, including the plain-language explanation shown on shortlist reveal.
"""

from pydantic import BaseModel, Field


class MatchFactorScore(BaseModel):
    """One component of the overall score, e.g. 'skills', 'location', 'seniority'."""

    factor: str
    score: float = Field(..., ge=0, le=1)
    detail: str = ""


class MatchResult(BaseModel):
    candidate_id: str
    job_posting_id: str
    overall_score: float = Field(..., ge=0, le=1)
    factor_scores: list[MatchFactorScore]
    explanation: str = Field(..., description="Plain-language summary, e.g. '87% match: strong skill overlap...'")
    shortlisted: bool = False
