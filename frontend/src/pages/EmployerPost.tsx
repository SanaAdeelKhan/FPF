import { useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { api, SeniorityLevel } from "../lib/api";

export default function EmployerPost() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [title, setTitle] = useState("");
  const [seniorityLevel, setSeniorityLevel] = useState<SeniorityLevel>("mid");
  const [yearsRequired, setYearsRequired] = useState(2);
  const [applyBy, setApplyBy] = useState("");

  const [fullDescription, setFullDescription] = useState("");
  const [requiredSkills, setRequiredSkills] = useState("");
  const [niceToHaveSkills, setNiceToHaveSkills] = useState("");
  const [onSite, setOnSite] = useState(false);
  const [location, setLocation] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const posting = await api.createPosting({
        title,
        seniority_level: seniorityLevel,
        years_experience_required: yearsRequired,
        apply_by: new Date(applyBy).toISOString(),
        hidden_requirements: {
          full_description: fullDescription,
          required_skills: requiredSkills.split(",").map((s) => s.trim()).filter(Boolean),
          nice_to_have_skills: niceToHaveSkills.split(",").map((s) => s.trim()).filter(Boolean),
          location: onSite ? location : null,
          on_site: onSite,
          min_years_experience: yearsRequired,
          other_notes: "",
        },
      });
      navigate(`/employer/dashboard/${posting.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="container">
      <h1>Post a role</h1>
      <p className="subtitle">Candidates will only ever see the title, seniority, and years required.</p>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="card">
          <div className="field">
            <label>Job title</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
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
            <label>Years of experience required</label>
            <input type="number" min={0} step={0.5} value={yearsRequired} onChange={(e) => setYearsRequired(Number(e.target.value))} required />
          </div>
          <div className="field">
            <label>Apply-by deadline</label>
            <input type="datetime-local" value={applyBy} onChange={(e) => setApplyBy(e.target.value)} required />
          </div>
        </div>

        <fieldset>
          <legend>Hidden from candidates until selected</legend>
          <div className="hidden-note">This is the real job description — candidates never see this pre-match.</div>
          <div className="field">
            <label>Full job description</label>
            <textarea value={fullDescription} onChange={(e) => setFullDescription(e.target.value)} required />
          </div>
          <div className="field">
            <label>Required skills (comma-separated)</label>
            <input value={requiredSkills} onChange={(e) => setRequiredSkills(e.target.value)} placeholder="python, fastapi" />
          </div>
          <div className="field">
            <label>Nice-to-have skills (comma-separated)</label>
            <input value={niceToHaveSkills} onChange={(e) => setNiceToHaveSkills(e.target.value)} placeholder="react" />
          </div>
          <div className="field">
            <label>
              <input type="checkbox" checked={onSite} onChange={(e) => setOnSite(e.target.checked)} style={{ width: "auto", marginRight: 8 }} />
              On-site role
            </label>
          </div>
          {onSite && (
            <div className="field">
              <label>Required location</label>
              <input value={location} onChange={(e) => setLocation(e.target.value)} />
            </div>
          )}
        </fieldset>

        <button type="submit" disabled={submitting}>
          {submitting ? "Posting..." : "Post role"}
        </button>
      </form>
    </div>
  );
}
