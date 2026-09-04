import { useParams, Link } from "react-router-dom";

// Simple confirmation after posting a role — surfaces the posting ID so it can be
// used to test matching (real employer flow would list candidates automatically;
// this manual-ID step is a deliberate demo/testing shortcut).

export default function PostingCreated() {
  const { postingId } = useParams();

  return (
    <div className="page">
      <h1>Role posted</h1>
      <p className="subtitle">Your listing is live. Candidates will only see the title, seniority, and years required.</p>
      <div className="id-box">
        <span className="id-label">Posting ID</span>
        <code>{postingId}</code>
      </div>
      <p>Use this ID to test matching against candidate uploads.</p>
      <Link to="/employer/postings" className="button-link">View all your postings →</Link>
      <br />
      <Link to="/candidate" className="button-link">Upload a test candidate</Link>
    </div>
  );
}
