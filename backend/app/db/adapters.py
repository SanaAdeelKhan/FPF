"""
Adapts DB-layer ORM rows (plain JSON dicts for parsed_profile/hidden_requirements,
plain strings for enums) into the Pydantic schemas app/services/matching_engine.py
and explainer.py were written and tested against (nested objects, real enums).

Deliberately kept separate from store.py: this is a schema-shape concern, not a
persistence concern, and keeping it isolated means the already-verified matching
engine never has to change to accommodate how the DB happens to store things.
"""

from app.db.orm_models import CandidateORM, JobPostingORM
from app.models.candidate import AvailabilityType, Candidate, ParsedCVProfile, SeniorityLevel
from app.models.employer import HiddenRequirements, JobPosting


def to_candidate_schema(candidate: CandidateORM) -> Candidate:
    return Candidate(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        location=candidate.location,
        seniority_level=SeniorityLevel(candidate.seniority_level),
        years_experience=candidate.years_experience,
        availability=AvailabilityType(candidate.availability),
        open_to_remote=candidate.open_to_remote,
        cv_raw_text=candidate.cv_raw_text,
        parsed_profile=ParsedCVProfile(**candidate.parsed_profile) if candidate.parsed_profile else None,
        created_at=candidate.created_at,
    )


def to_posting_schema(posting: JobPostingORM) -> JobPosting:
    return JobPosting(
        id=posting.id,
        title=posting.title,
        seniority_level=SeniorityLevel(posting.seniority_level),
        years_experience_required=posting.years_experience_required,
        company_name=posting.company.name,
        apply_by=posting.apply_by,
        hidden_requirements=HiddenRequirements(**posting.hidden_requirements),
        created_at=posting.created_at,
    )
