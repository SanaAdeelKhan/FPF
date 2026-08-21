import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import EmployerPost from "./pages/EmployerPost";
import CandidateUpload from "./pages/CandidateUpload";
import ShortlistReveal from "./pages/ShortlistReveal";

export default function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/employer">Post a role</Link>
        {" | "}
        <Link to="/candidate">Upload CV</Link>
      </nav>
      <Routes>
        <Route path="/employer" element={<EmployerPost />} />
        <Route path="/candidate" element={<CandidateUpload />} />
        <Route path="/match/:candidateId/:postingId" element={<ShortlistReveal />} />
        <Route path="/" element={<CandidateUpload />} />
      </Routes>
    </BrowserRouter>
  );
}
