import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api, Candidate } from "../lib/api";

// After upload, show the AI-parsed profile back to the candidate (transparency
// works both ways — they should see what the system extracted from their CV),
// then let them test a match against a posting ID.

export default function CandidateUploaded() {
  const { candidateId } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [postingId, setPostingId] = useState("");

  useEffect(() => {
    if (!candidateId) return;
    fetch(`${import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"}/candidates/${candidateId}`)
      .then((r) => r.json())
      .then(setCandidate)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load candidate"));
  }, [candidateId]);

  function goToMatch() {
    if (candidateId && postingId) navigate(`/match/${candidateId}/${postingId}`);
  }

  if (error) return <div className="page"><p className="error">{error}</p></div>;
  if (!candidate) return <div className="page"><p>Loading…</p></div>;

  const profile = candidate.parsed_profile;

  return (
    <div className="page">
      <h1>CV received</h1>
      <p className="subtitle">Here's what our AI extracted from your CV:</p>

      {profile && profile.skills.length === 0 && profile.key_strengths.length === 0 ? (
        <p className="error">CV parsing didn't return results — you can still test matching manually.</p>
      ) : (
        <div className="profile-summary">
          <p>{profile?.summary}</p>
          <h3>Skills</h3>
          <ul className="tag-list">{profile?.skills.map((s) => <li key={s}>{s}</li>)}</ul>
          <h3>What you're best at</h3>
          <ul>{profile?.key_strengths.map((s) => <li key={s}>{s}</li>)}</ul>
        </div>
      )}

      <section className="section">
        <label>
          Posting ID to test a match against
          <input value={postingId} onChange={(e) => setPostingId(e.target.value)} placeholder="paste a posting ID" />
        </label>
        <button onClick={goToMatch} disabled={!postingId}>
          Run match
        </button>
      </section>
    </div>
  );
}
