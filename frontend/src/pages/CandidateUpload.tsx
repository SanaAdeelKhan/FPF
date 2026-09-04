import { useState, FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, AvailabilityType, SeniorityLevel } from "../lib/api";
import { useAuth } from "../lib/auth";

export default function CandidateUpload() {
  const { postingId } = useParams<{ postingId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [fullName, setFullName] = useState(user?.fullName ?? "");
  // Email is locked to the logged-in candidate's account email. The backend
  // upserts a candidate profile by email, so this MUST match the email used at
  // signup — otherwise CV data would land on a new, orphaned profile instead of
  // the one tied to this session's token.
  const email = user?.email ?? "";
  const [location, setLocation] = useState("");
  const [seniorityLevel, setSeniorityLevel] = useState<SeniorityLevel>("mid");
  const [yearsExperience, setYearsExperience] = useState(2);
  const [availability, setAvailability] = useState<AvailabilityType>("immediate");
  const [openToRemote, setOpenToRemote] = useState(true);
  const [cvText, setCvText] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!postingId) return;
    setError(null);
    setSubmitting(true);
    try {
      await api.uploadCandidate({
        full_name: fullName,
        email,
        location,
        seniority_level: seniorityLevel,
        years_experience: yearsExperience,
        availability,
        open_to_remote: openToRemote,
        cv_raw_text: cvText,
      });
      await api.applyToPosting(postingId);
      navigate(`/status/${postingId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="container">
      <h1>Tell us what you're best at</h1>
      <p className="subtitle">No job description to reverse-engineer — just describe your actual strengths.</p>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="card">
          <div className="field">
            <label>Full name</label>
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
          </div>
          <div className="field">
            <label>Email</label>
            <input type="email" value={email} disabled />
          </div>
          <div className="field">
            <label>Location (city, country)</label>
            <input value={location} onChange={(e) => setLocation(e.target.value)} required />
          </div>
          <div className="field">
            <label>Seniority level</label>
            <select value={seniorityLevel} onChange={(e) => setSeniorityLevel(e.target.value as SeniorityLevel)}>
              <option value="fresh_grad">Fresh grad</option>
              <option value="mid">Mid</option>
              <option value="senior">Senior</option>
            </select>
          </div>
          <div className="field">
            <label>Years of experience</label>
            <input type="number" min={0} step={0.5} value={yearsExperience} onChange={(e) => setYearsExperience(Number(e.target.value))} required />
          </div>
          <div className="field">
            <label>Availability</label>
            <select value={availability} onChange={(e) => setAvailability(e.target.value as AvailabilityType)}>
              <option value="immediate">Immediate</option>
              <option value="two_weeks">Two weeks' notice</option>
              <option value="one_month">One month's notice</option>
              <option value="flexible">Flexible</option>
            </select>
          </div>
          <div className="field">
            <label>
              <input type="checkbox" checked={openToRemote} onChange={(e) => setOpenToRemote(e.target.checked)} style={{ width: "auto", marginRight: 8 }} />
              Open to remote
            </label>
          </div>
          <div className="field">
            <label>Paste your CV text</label>
            <textarea value={cvText} onChange={(e) => setCvText(e.target.value)} required placeholder="Paste your 2-page CV here..." />
          </div>
        </div>

        <button type="submit" disabled={submitting}>
          {submitting ? "Submitting..." : "Submit & apply"}
        </button>
      </form>
    </div>
  );
}
