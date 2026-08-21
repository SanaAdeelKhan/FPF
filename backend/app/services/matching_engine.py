"""
Matching engine: scores a parsed candidate profile against a job posting's hidden
requirements across multiple factors, then combines them into an overall score.

Deliberately rule-based, not LLM-based: scoring needs to be fast, free, and
deterministic so the same candidate+posting pair always produces the same score —
that consistency matters for both the demo and for candidates trusting the result.
The LLM budget is spent on cv_parser (extraction) and, optionally, explainer
(phrasing) instead.
"""

from app.models.candidate import Candidate, SeniorityLevel
from app.models.employer import JobPosting
from app.models.match import MatchFactorScore

FACTOR_WEIGHTS = {
    "skills": 0.45,
    "location": 0.20,
    "seniority": 0.20,
    "availability": 0.15,
}

# Ordered so "distance" between levels can be computed numerically
_SENIORITY_ORDER = [SeniorityLevel.fresh_grad, SeniorityLevel.mid, SeniorityLevel.senior]

_AVAILABILITY_SCORE = {
    "immediate": 1.0,
    "two_weeks": 0.85,
    "one_month": 0.6,
    "flexible": 0.75,
}


def _normalize(text: str) -> str:
    return text.strip().lower()


def score_skills(candidate: Candidate, posting: JobPosting) -> MatchFactorScore:
    required = {_normalize(s) for s in posting.hidden_requirements.required_skills}
    nice_to_have = {_normalize(s) for s in posting.hidden_requirements.nice_to_have_skills}
    candidate_skills = {_normalize(s) for s in (candidate.parsed_profile.skills if candidate.parsed_profile else [])}

    if not required and not nice_to_have:
        return MatchFactorScore(factor="skills", score=1.0, detail="No specific skills required")

    required_hits = required & candidate_skills
    nice_hits = nice_to_have & candidate_skills

    required_score = (len(required_hits) / len(required)) if required else 1.0
    nice_bonus = (len(nice_hits) / len(nice_to_have)) * 0.15 if nice_to_have else 0.0
    score = min(1.0, required_score + nice_bonus)

    if required_hits:
        detail = f"Matches {len(required_hits)}/{len(required)} required skills: {', '.join(sorted(required_hits))}"
    else:
        detail = "No overlap with required skills"
    return MatchFactorScore(factor="skills", score=round(score, 2), detail=detail)


def score_location(candidate: Candidate, posting: JobPosting) -> MatchFactorScore:
    req = posting.hidden_requirements
    if not req.on_site:
        return MatchFactorScore(factor="location", score=1.0, detail="Remote-friendly role, location not a constraint")

    if not req.location:
        return MatchFactorScore(factor="location", score=0.5, detail="Role marked on-site but no location specified")

    if _normalize(candidate.location) == _normalize(req.location):
        return MatchFactorScore(factor="location", score=1.0, detail=f"Located in {req.location} as required")

    return MatchFactorScore(
        factor="location", score=0.1, detail=f"On-site role requires {req.location}; candidate is in {candidate.location}"
    )


def score_seniority(candidate: Candidate, posting: JobPosting) -> MatchFactorScore:
    try:
        cand_idx = _SENIORITY_ORDER.index(candidate.seniority_level)
        post_idx = _SENIORITY_ORDER.index(posting.seniority_level)
    except ValueError:
        return MatchFactorScore(factor="seniority", score=0.5, detail="Unrecognized seniority level")

    level_distance = abs(cand_idx - post_idx)
    level_score = {0: 1.0, 1: 0.5, 2: 0.1}.get(level_distance, 0.1)

    years_required = posting.years_experience_required
    years_score = 1.0 if candidate.years_experience >= years_required else max(
        0.0, candidate.years_experience / years_required if years_required > 0 else 1.0
    )

    score = round((level_score * 0.6) + (years_score * 0.4), 2)
    detail = (
        f"{candidate.seniority_level.value} candidate ({candidate.years_experience} yrs) "
        f"vs {posting.seniority_level.value} role ({years_required} yrs required)"
    )
    return MatchFactorScore(factor="seniority", score=score, detail=detail)


def score_availability(candidate: Candidate, posting: JobPosting) -> MatchFactorScore:
    score = _AVAILABILITY_SCORE.get(candidate.availability.value, 0.5)
    return MatchFactorScore(factor="availability", score=score, detail=f"Availability: {candidate.availability.value}")


def compute_match(candidate: Candidate, posting: JobPosting) -> tuple[float, list[MatchFactorScore]]:
    """Returns (overall_score, factor_scores), overall = weighted sum via FACTOR_WEIGHTS."""
    factor_scores = [
        score_skills(candidate, posting),
        score_location(candidate, posting),
        score_seniority(candidate, posting),
        score_availability(candidate, posting),
    ]
    overall = sum(f.score * FACTOR_WEIGHTS[f.factor] for f in factor_scores)
    return round(overall, 2), factor_scores
