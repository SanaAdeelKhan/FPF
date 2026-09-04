"""
Deadline close-out: the mechanism behind "every candidate gets a definitive
answer, no one waits in silence."

No cron/scheduler infrastructure needed for the hackathon build — instead this
runs as a cheap check-on-access: any time a posting or a candidate's
applications are read, first call `close_if_past_deadline` (or
`close_all_due_postings` for a batch sweep). Once a posting is closed once,
`closed=True` short-circuits every future call, so this stays O(1) on the
common path.

This keeps the guarantee real (no application sits at `pending` past its
posting's apply_by) without needing Celery/APScheduler/etc — appropriate for a
hackathon timeline; swapping in a real scheduler later doesn't change this
function's logic, only what calls it.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db import store
from app.db.orm_models import ApplicationStatus, JobPostingORM


def _as_utc(dt: datetime) -> datetime:
    """SQLite drops tzinfo on round-trip even for DateTime(timezone=True) columns,
    so a value we stored as UTC-aware can come back naive. Every apply_by we ever
    write is UTC, so a naive read is always UTC — just re-attach the tzinfo."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def close_if_past_deadline(db: Session, posting: JobPostingORM) -> JobPostingORM:
    """Resolve every pending application for this posting if its deadline has passed."""
    if posting.closed:
        return posting
    if _as_utc(posting.apply_by) > datetime.now(timezone.utc):
        return posting

    applications = store.list_applications_for_posting(db, posting.id)
    for application in applications:
        if application.status != ApplicationStatus.pending:
            continue  # already resolved (e.g. manually), don't touch it
        new_status = (
            ApplicationStatus.selected if application.shortlisted else ApplicationStatus.not_selected
        )
        store.resolve_application(db, application, new_status)

    posting.closed = True
    posting.closed_at = datetime.now(timezone.utc)
    db.add(posting)
    db.commit()
    db.refresh(posting)
    return posting


def close_all_due_postings(db: Session) -> list[JobPostingORM]:
    """Batch sweep — call this on a schedule (or a manual admin button) to close
    out every posting whose deadline has passed, not just the one being viewed."""
    due = store.list_postings_past_deadline_unclosed(db)
    return [close_if_past_deadline(db, posting) for posting in due]
