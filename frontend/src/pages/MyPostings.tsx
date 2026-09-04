import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, JobPostingPublic } from "../lib/api";

const SENIORITY_LABEL: Record<string, string> = {
  fresh_grad: "Fresh grad",
  mid: "Mid",
  senior: "Senior",
};

export default function MyPostings() {
  const navigate = useNavigate();
  const [postings, setPostings] = useState<JobPostingPublic[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listMyPostings()
      .then(setPostings)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load postings"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="container">
      <h1>My postings</h1>
      <p className="subtitle">
        <Link to="/employer">Post another role</Link>
      </p>

      {error && <div className="error">{error}</div>}
      {loading && <p>Loading...</p>}

      {!loading && postings.length === 0 && <p>You haven't posted any roles yet.</p>}

      {postings.map((p) => (
        <div className="card posting-item" key={p.id} onClick={() => navigate(`/employer/dashboard/${p.id}`)}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <strong>{p.title}</strong>
            <span className={`badge ${p.closed ? "badge-not_selected" : "badge-pending"}`}>
              {p.closed ? "Closed" : "Open"}
            </span>
          </div>
          <div className="hidden-note" style={{ marginTop: 6 }}>
            {SENIORITY_LABEL[p.seniority_level]} · {p.years_experience_required}+ yrs · Apply by{" "}
            {new Date(p.apply_by).toLocaleDateString()}
          </div>
        </div>
      ))}
    </div>
  );
}
