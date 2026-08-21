// Thin fetch wrapper around the backend. Every page imports from here rather than
// calling fetch() directly, so the base URL and error handling live in one place.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export interface JobPostingPublic {
  id: string;
  title: string;
  seniority_level: "fresh_grad" | "mid" | "senior";
  years_experience_required: number;
  company_name: string;
  created_at: string;
}

export interface MatchResult {
  candidate_id: string;
  job_posting_id: string;
  overall_score: number;
  factor_scores: { factor: string; score: number; detail: string }[];
  explanation: string;
  shortlisted: boolean;
}

// TODO: fill in request bodies to match backend Pydantic schemas as routes are implemented
export const api = {
  createPosting: (body: unknown) =>
    request<JobPostingPublic>("/employers/postings", { method: "POST", body: JSON.stringify(body) }),

  uploadCandidate: (body: unknown) => request<{ id: string }>("/candidates", { method: "POST", body: JSON.stringify(body) }),

  runMatch: (candidateId: string, postingId: string) =>
    request<MatchResult>(`/matching/run/${candidateId}/${postingId}`, { method: "POST" }),

  revealJd: (candidateId: string, postingId: string) =>
    request<{ full_description: string }>(`/matching/reveal/${candidateId}/${postingId}`),
};
