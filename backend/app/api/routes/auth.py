"""
Auth endpoints: separate signup for candidates and employers, shared login
(looks up by email in whichever table matches), and /auth/me to check the
current session. Tokens are plain bearer JWTs returned in the response body —
frontend stores it (e.g. localStorage) and sends it as Authorization: Bearer <token>.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.orm_models import CandidateORM, Company
from app.db.session import get_db
from app.models.auth import CandidateSignup, EmployerSignup, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup/candidate", response_model=TokenResponse)
def signup_candidate(payload: CandidateSignup, db: Session = Depends(get_db)):
    existing = db.query(CandidateORM).filter(CandidateORM.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    candidate = CandidateORM(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        # Placeholder profile fields — real values get filled in when they upload a CV.
        location="",
        seniority_level="",
        years_experience=0,
        availability="",
        open_to_remote=True,
        cv_raw_text="",
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    token = create_access_token(subject=candidate.id, role="candidate")
    return TokenResponse(access_token=token, role="candidate", id=candidate.id)


@router.post("/signup/employer", response_model=TokenResponse)
def signup_employer(payload: EmployerSignup, db: Session = Depends(get_db)):
    existing_email = db.query(Company).filter(Company.email == payload.email).first()
    if existing_email is not None:
        raise HTTPException(status_code=400, detail="An account with this email already exists")
    existing_name = db.query(Company).filter(Company.name == payload.company_name).first()
    if existing_name is not None:
        raise HTTPException(status_code=400, detail="A company with this name already exists")

    company = Company(
        name=payload.company_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(company)
    db.commit()
    db.refresh(company)

    token = create_access_token(subject=company.id, role="employer")
    return TokenResponse(access_token=token, role="employer", id=company.id)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    candidate = db.query(CandidateORM).filter(CandidateORM.email == payload.email).first()
    if candidate is not None and candidate.password_hash is not None:
        if verify_password(payload.password, candidate.password_hash):
            token = create_access_token(subject=candidate.id, role="candidate")
            return TokenResponse(access_token=token, role="candidate", id=candidate.id)

    company = db.query(Company).filter(Company.email == payload.email).first()
    if company is not None and company.password_hash is not None:
        if verify_password(payload.password, company.password_hash):
            token = create_access_token(subject=company.id, role="employer")
            return TokenResponse(access_token=token, role="employer", id=company.id)

    raise HTTPException(status_code=401, detail="Invalid email or password")
