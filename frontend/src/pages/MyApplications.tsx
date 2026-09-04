import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, CandidateApplicationSummary } from "../lib/api";

const STATUS_LABEL: Record<string, string> = {
  pending: "Pending",
  selected: "Selected",
  not_selected: "Not selected",
};

export default function MyApplications() {
  const navigate = useNavigate();
  const [applications, setApplications] = useState<CandidateApplicationSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listMyApplications()
      .then(setApplications)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load applications"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="container">
      <h1>My applications</h1>
      <p className="subtitle">
        <Link to="/jobs">Browse more roles</Link>
      </p>

      {error && <div className="error">{error}</div>}
      {loading && <p>Loading...</p>}

      {!loading && applications.length === 0 && <p>You haven't applied to anything yet.</p>}

      {applications.map((a) => (
        <div className="card posting-item" key={a.application_id} onClick={() => navigate(`/status/${a.job_posting_id}`)}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <strong>{a.job_title}</strong>
            <span className={`badge badge-${a.status}`}>{STATUS_LABEL[a.status]}</span>
          </div>
          <div className="hidden-note" style={{ marginTop: 6 }}>
            {a.company_name} · Applied {new Date(a.applied_at).toLocaleDateString()} · Apply-by{" "}
            {new Date(a.apply_by).toLocaleDateString()}
          </div>
        </div>
      ))}
    </div>
  );
}
