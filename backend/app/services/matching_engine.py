"""
Matching engine: scores a parsed candidate profile against a job posting's hidden
requirements across multiple factors, then combines them into an overall score.

Design intent: each factor is scored independently (0-1) and returned alongside
the combined score, so the transparency layer (explainer.py) has real numbers to
turn into plain language instead of inventing a justification after the fact.
"""

from app.models.candidate import Candidate
from app.models.employer import JobPosting
from app.models.match import MatchFactorScore

# Tune these once real scoring is in place and validated against mock data.
FACTOR_WEIGHTS = {
    "skills": 0.45,
    "location": 0.20,
    "seniority": 0.20,
    "availability": 0.15,
}


def score_skills(candidate: Candidate, posting: JobPosting) -> MatchFactorScore:
    raise NotImplementedError("matching_engine.score_skills: overlap between parsed skills and required_skills")


def score_location(candidate: Candidate, posting: JobPosting) -> MatchFactorScore:
    raise NotImplementedError("matching_engine.score_location: only penalize if posting.on_site is True")


def score_seniority(candidate: Candidate, posting: JobPosting) -> MatchFactorScore:
    raise NotImplementedError("matching_engine.score_seniority: compare seniority_level + years_experience")


def score_availability(candidate: Candidate, posting: JobPosting) -> MatchFactorScore:
    raise NotImplementedError("matching_engine.score_availability: compare availability against posting urgency")


def compute_match(candidate: Candidate, posting: JobPosting) -> tuple[float, list[MatchFactorScore]]:
    """
    Returns (overall_score, factor_scores). Overall score is the weighted sum of
    factor scores using FACTOR_WEIGHTS.
    """
    factor_scores = [
        score_skills(candidate, posting),
        score_location(candidate, posting),
        score_seniority(candidate, posting),
        score_availability(candidate, posting),
    ]
    overall = sum(f.score * FACTOR_WEIGHTS[f.factor] for f in factor_scores)
    return overall, factor_scores
