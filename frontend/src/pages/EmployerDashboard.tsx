import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, EmployerApplicantView } from "../lib/api";

const STATUS_LABEL: Record<string, string> = {
  pending: "Pending",
  selected: "Selected",
  not_selected: "Not selected",
};

export default function EmployerDashboard() {
  const { postingId } = useParams<{ postingId: string }>();
  const [applicants, setApplicants] = useState<EmployerApplicantView[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!postingId) return;
    api
      .listApplicants(postingId)
      .then(setApplicants)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load applicants"))
      .finally(() => setLoading(false));
  }, [postingId]);

  return (
    <div className="container">
      <h1>Applicants</h1>
      <p className="subtitle">
        Statuses resolve automatically once the posting's deadline passes.{" "}
        <Link to="/my-postings">My postings</Link> · <Link to="/employer">Post another role</Link>
      </p>

      {error && <div className="error">{error}</div>}
      {loading && <p>Loading...</p>}

      {!loading && applicants.length === 0 && <p>No applicants yet.</p>}

      {applicants.map((a) => (
        <div className="card" key={a.application_id}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <strong>{a.candidate_name}</strong>
            <span className={`badge badge-${a.status}`}>{STATUS_LABEL[a.status]}</span>
          </div>
          <div className="hidden-note" style={{ marginTop: 8 }}>
            Match score: {Math.round(a.overall_score * 100)}% — applied {new Date(a.applied_at).toLocaleDateString()}
          </div>
        </div>
      ))}
    </div>
  );
}
