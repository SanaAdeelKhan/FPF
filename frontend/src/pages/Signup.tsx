import { useState, FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { Role } from "../lib/api";

export default function Signup() {
  const navigate = useNavigate();
  const { signupCandidate, signupEmployer } = useAuth();
  const [role, setRole] = useState<Role>("candidate");
  const [name, setName] = useState(""); // full name (candidate) or company name (employer)
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (role === "candidate") {
        await signupCandidate(name, email, password);
        navigate("/jobs");
      } else {
        await signupEmployer(name, email, password);
        navigate("/employer");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="container">
      <h1>Sign up</h1>

      <div className="field">
        <label>I am a...</label>
        <select value={role} onChange={(e) => setRole(e.target.value as Role)}>
          <option value="candidate">Candidate</option>
          <option value="employer">Employer</option>
        </select>
      </div>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="card">
          <div className="field">
            <label>{role === "candidate" ? "Full name" : "Company name"}</label>
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="field">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="field">
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
          </div>
        </div>
        <button type="submit" disabled={submitting}>
          {submitting ? "Signing up..." : "Sign up"}
        </button>
      </form>

      <p className="subtitle" style={{ marginTop: 16 }}>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
