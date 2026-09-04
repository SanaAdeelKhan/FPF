import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApplicationStatusView } from "../lib/api";

export default function ApplicationStatusPage() {
  const { postingId } = useParams<{ postingId: string }>();
  const [statusView, setStatusView] = useState<ApplicationStatusView | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function refresh() {
    if (!postingId) return;
    setLoading(true);
    api
      .getApplicationStatus(postingId)
      .then(setStatusView)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load status"))
      .finally(() => setLoading(false));
  }

  useEffect(refresh, [postingId]);

  if (loading) return <div className="container"><p>Loading...</p></div>;
  if (error) return <div className="container"><div className="error">{error}</div></div>;
  if (!statusView) return null;

  return (
    <div className="container">
      <h1>{statusView.job_title}</h1>
      <p className="subtitle">
        {statusView.company_name} · <Link to="/jobs">Browse more roles</Link> · <Link to="/my-applications">My applications</Link>
      </p>

      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span className={`badge badge-${statusView.status}`}>
            {statusView.status === "pending" ? "Pending" : statusView.status === "selected" ? "Selected" : "Not selected"}
          </span>
          {!loading && statusView.status === "pending" && (
            <button onClick={refresh} style={{ fontSize: "0.85rem", padding: "6px 12px" }}>
              Check again
            </button>
          )}
        </div>
        <p style={{ marginTop: 16 }}>{statusView.message}</p>

        {statusView.overall_score !== null && (
          <>
            <div style={{ marginTop: 16, fontWeight: 600 }}>
              Match score: {Math.round(statusView.overall_score * 100)}%
            </div>
            {statusView.explanation && <p className="hidden-note">{statusView.explanation}</p>}
            {statusView.factor_scores && (
              <div style={{ marginTop: 12 }}>
                {statusView.factor_scores.map((f) => (
                  <div className="factor-row" key={f.factor}>
                    <span style={{ textTransform: "capitalize" }}>{f.factor}</span>
                    <span>{Math.round(f.score * 100)}% — {f.detail}</span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {statusView.status === "selected" && statusView.hidden_requirements && (
        <div className="jd-reveal">
          <strong>Full job description</strong>
          <p style={{ marginTop: 10 }}>{statusView.hidden_requirements.full_description}</p>
          {statusView.hidden_requirements.required_skills.length > 0 && (
            <p className="hidden-note">
              Required skills: {statusView.hidden_requirements.required_skills.join(", ")}
            </p>
          )}
          {statusView.hidden_requirements.on_site && statusView.hidden_requirements.location && (
            <p className="hidden-note">On-site in {statusView.hidden_requirements.location}</p>
          )}
        </div>
      )}
    </div>
  );
}
