// Thin fetch wrapper around the backend. Every page imports from here rather than
// calling fetch() directly, so the base URL, auth header, and error handling all
// live in one place.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const AUTH_STORAGE_KEY = "fpf_auth";

export type Role = "candidate" | "employer";

export interface StoredUser {
  token: string;
  role: Role;
  id: string;
  email: string;
  fullName?: string;
}

export function getStoredUser(): StoredUser | null {
  const raw = localStorage.getItem(AUTH_STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredUser;
  } catch {
    return null;
  }
}

export function setStoredUser(user: StoredUser) {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(user));
}

export function clearStoredUser() {
  localStorage.removeItem(AUTH_STORAGE_KEY);
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const stored = getStoredUser();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (stored) {
    headers["Authorization"] = `Bearer ${stored.token}`;
  }
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers,
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export type SeniorityLevel = "fresh_grad" | "mid" | "senior";
export type AvailabilityType = "immediate" | "two_weeks" | "one_month" | "flexible";
export type ApplicationStatus = "pending" | "selected" | "not_selected";

export interface HiddenRequirements {
  full_description: string;
  required_skills: string[];
  nice_to_have_skills: string[];
  location: string | null;
  on_site: boolean;
  min_years_experience: number;
  other_notes: string;
}

// company_name removed — the posting's company is the logged-in employer, from the
// auth token, never a client-supplied string.
export interface JobPostingCreate {
  title: string;
  seniority_level: SeniorityLevel;
  years_experience_required: number;
  apply_by: string; // ISO datetime
  hidden_requirements: HiddenRequirements;
}

export interface JobPostingPublic {
  id: string;
  title: string;
  seniority_level: SeniorityLevel;
  years_experience_required: number;
  company_name: string;
  apply_by: string;
  closed: boolean;
  created_at: string;
}

export interface CandidateCreate {
  full_name: string;
  email: string;
  location: string;
  seniority_level: SeniorityLevel;
  years_experience: number;
  availability: AvailabilityType;
  open_to_remote: boolean;
  cv_raw_text: string;
}

export interface ParsedCVProfile {
  skills: string[];
  years_experience_inferred: number | null;
  key_strengths: string[];
  past_roles: string[];
  summary: string;
}

export interface Candidate extends CandidateCreate {
  id: string;
  parsed_profile: ParsedCVProfile | null;
  created_at: string;
}

export interface ApplyResponse {
  application_id: string;
  status: ApplicationStatus;
  apply_by: string;
  message: string;
}

export interface MatchFactorScore {
  factor: string;
  score: number;
  detail: string;
}

export interface ApplicationStatusView {
  application_id: string;
  job_title: string;
  company_name: string;
  status: ApplicationStatus;
  apply_by: string;
  overall_score: number | null;
  factor_scores: MatchFactorScore[] | null;
  explanation: string | null;
  hidden_requirements: HiddenRequirements | null;
  message: string;
}

export interface EmployerApplicantView {
  application_id: string;
  candidate_id: string;
  candidate_name: string;
  status: ApplicationStatus;
  overall_score: number;
  applied_at: string;
}

export interface CandidateApplicationSummary {
  application_id: string;
  job_posting_id: string;
  job_title: string;
  company_name: string;
  status: ApplicationStatus;
  apply_by: string;
  applied_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: Role;
  id: string;
}

export const api = {
  // --- Auth ---
  login: (body: { email: string; password: string }) =>
    request<TokenResponse>("/auth/login", { method: "POST", body: JSON.stringify(body) }),

  signupCandidate: (body: { full_name: string; email: string; password: string }) =>
    request<TokenResponse>("/auth/signup/candidate", { method: "POST", body: JSON.stringify(body) }),

  signupEmployer: (body: { company_name: string; email: string; password: string }) =>
    request<TokenResponse>("/auth/signup/employer", { method: "POST", body: JSON.stringify(body) }),

  // --- Employer ---
  createPosting: (body: JobPostingCreate) =>
    request<JobPostingPublic>("/employers/postings", { method: "POST", body: JSON.stringify(body) }),

  listPostings: () => request<JobPostingPublic[]>("/employers/postings"),

  listMyPostings: () => request<JobPostingPublic[]>("/employers/me/postings"),

  listApplicants: (postingId: string) =>
    request<EmployerApplicantView[]>(`/employers/postings/${postingId}/applicants`),

  // --- Candidate ---
  uploadCandidate: (body: CandidateCreate) =>
    request<Candidate>("/candidates", { method: "POST", body: JSON.stringify(body) }),

  listMyApplications: () => request<CandidateApplicationSummary[]>("/candidates/me/applications"),

  // --- Matching (candidate_id now comes from the auth token, not the URL) ---
  applyToPosting: (postingId: string) =>
    request<ApplyResponse>(`/matching/apply/${postingId}`, { method: "POST" }),

  getApplicationStatus: (postingId: string) =>
    request<ApplicationStatusView>(`/matching/status/${postingId}`),
};
