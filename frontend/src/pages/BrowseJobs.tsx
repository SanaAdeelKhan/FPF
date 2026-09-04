import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, JobPostingPublic, CandidateApplicationSummary } from "../lib/api";
import { useAuth } from "../lib/auth";

const SENIORITY_LABEL: Record<string, string> = {
  fresh_grad: "Fresh grad",
  mid: "Mid",
  senior: "Senior",
};

const STATUS_LABEL: Record<string, string> = {
  pending: "Applied — pending",
  selected: "Applied — selected",
  not_selected: "Applied — not selected",
};

export default function BrowseJobs() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [postings, setPostings] = useState<JobPostingPublic[]>([]);
  const [myApplications, setMyApplications] = useState<CandidateApplicationSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.listPostings(),
      user?.role === "candidate" ? api.listMyApplications() : Promise.resolve([]),
    ])
      .then(([postingsRes, applicationsRes]) => {
        setPostings(postingsRes);
        setMyApplications(applicationsRes);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load postings"))
      .finally(() => setLoading(false));
  }, [user]);

  const appliedByPostingId = new Map(myApplications.map((a) => [a.job_posting_id, a]));

  return (
    <div className="container">
      <h1>Open roles</h1>
      <p className="subtitle">
        Titles only — the full job description unlocks once you're matched and selected.{" "}
        <Link to="/">Back home</Link>
        {user?.role === "candidate" && (
          <>
            {" "}· <Link to="/my-applications">My applications</Link>
          </>
        )}
      </p>

      {error && <div className="error">{error}</div>}
      {loading && <p>Loading...</p>}

      {!loading && postings.length === 0 && <p>No open roles right now — check back soon.</p>}

      {postings.map((p) => {
        const applied = appliedByPostingId.get(p.id);
        return (
          <div
            className="card posting-item"
            key={p.id}
            onClick={() => navigate(applied ? `/status/${p.id}` : `/candidate/${p.id}`)}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <strong>{p.title}</strong>
              {applied && <span className={`badge badge-${applied.status}`}>{STATUS_LABEL[applied.status]}</span>}
            </div>
            <div className="hidden-note" style={{ marginTop: 6 }}>
              {p.company_name} · {SENIORITY_LABEL[p.seniority_level]} · {p.years_experience_required}+ yrs · Apply by{" "}
              {new Date(p.apply_by).toLocaleDateString()}
            </div>
          </div>
        );
      })}
    </div>
  );
}
