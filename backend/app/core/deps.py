"""
FastAPI dependencies that extract "who is making this request" from the
Authorization: Bearer <token> header, verify the role matches, and return the
actual DB row — so routes stop trusting raw IDs from the URL for anything
sensitive and instead trust the session.
"""

import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.orm_models import CandidateORM, Company
from app.db.session import get_db


def _get_token_payload(authorization: str | None = Header(default=None)) -> dict:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        return decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_candidate(
    payload: dict = Depends(_get_token_payload), db: Session = Depends(get_db)
) -> CandidateORM:
    if payload.get("role") != "candidate":
        raise HTTPException(status_code=403, detail="This action requires a candidate account")
    candidate = db.query(CandidateORM).filter(CandidateORM.id == payload["sub"]).first()
    if candidate is None:
        raise HTTPException(status_code=401, detail="Candidate account no longer exists")
    return candidate


def get_current_employer(
    payload: dict = Depends(_get_token_payload), db: Session = Depends(get_db)
) -> Company:
    if payload.get("role") != "employer":
        raise HTTPException(status_code=403, detail="This action requires an employer account")
    company = db.query(Company).filter(Company.id == payload["sub"]).first()
    if company is None:
        raise HTTPException(status_code=401, detail="Employer account no longer exists")
    return company
