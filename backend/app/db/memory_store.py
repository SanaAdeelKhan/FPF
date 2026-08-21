"""
In-memory data store — a deliberate shortcut to get the full pipeline (post ->
upload -> parse -> match -> reveal) working end-to-end fast, without spending
hackathon time on SQLAlchemy models/migrations up front.

Swap-out plan: every function here has a narrow, obvious signature (store/get by
id). When there's time, replace the dict-backed implementation with real
SQLAlchemy queries against app/db/session.py — routes.py callers don't need to
change, only this file's internals.

NOTE: data does not survive a server restart. Fine for local dev/demo; not fine
for anything resembling production.
"""

import uuid
from datetime import datetime, timezone

from app.models.candidate import Candidate, CandidateCreate
from app.models.employer import JobPosting, JobPostingCreate
from app.models.match import MatchResult

_candidates: dict[str, Candidate] = {}
_postings: dict[str, JobPosting] = {}
_matches: dict[str, MatchResult] = {}  # keyed by f"{candidate_id}:{posting_id}"


def new_id() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now(timezone.utc)


# --- candidates ---

def save_candidate(data: CandidateCreate) -> Candidate:
    candidate = Candidate(id=new_id(), created_at=now(), parsed_profile=None, **data.model_dump())
    _candidates[candidate.id] = candidate
    return candidate


def get_candidate(candidate_id: str) -> Candidate | None:
    return _candidates.get(candidate_id)


def update_candidate(candidate: Candidate) -> None:
    _candidates[candidate.id] = candidate


# --- postings ---

def save_posting(data: JobPostingCreate) -> JobPosting:
    posting = JobPosting(id=new_id(), created_at=now(), **data.model_dump())
    _postings[posting.id] = posting
    return posting


def get_posting(posting_id: str) -> JobPosting | None:
    return _postings.get(posting_id)


# --- matches ---

def save_match(match: MatchResult) -> None:
    _matches[f"{match.candidate_id}:{match.job_posting_id}"] = match


def get_match(candidate_id: str, posting_id: str) -> MatchResult | None:
    return _matches.get(f"{candidate_id}:{posting_id}")


def get_shortlist_for_posting(posting_id: str) -> list[MatchResult]:
    return [m for m in _matches.values() if m.job_posting_id == posting_id and m.shortlisted]
