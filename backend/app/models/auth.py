from pydantic import BaseModel, EmailStr


class CandidateSignup(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class EmployerSignup(BaseModel):
    company_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    id: str  # candidate_id or company_id
