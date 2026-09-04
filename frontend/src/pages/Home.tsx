import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="container">
      <h1>FPF — Finding Perfect Fit</h1>
      <p className="subtitle">A fair-hiring platform that hides the JD until the match is proven.</p>
      <div className="role-picker">
        <Link to="/employer">I'm hiring — post a role</Link>
        <Link to="/jobs">I'm a candidate — browse jobs</Link>
      </div>
    </div>
  );
}
