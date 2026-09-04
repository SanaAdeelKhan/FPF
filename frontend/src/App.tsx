import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./lib/auth";
import ProtectedRoute from "./components/ProtectedRoute";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import EmployerPost from "./pages/EmployerPost";
import EmployerDashboard from "./pages/EmployerDashboard";
import MyPostings from "./pages/MyPostings";
import BrowseJobs from "./pages/BrowseJobs";
import CandidateUpload from "./pages/CandidateUpload";
import ApplicationStatusPage from "./pages/ApplicationStatusPage";
import MyApplications from "./pages/MyApplications";

function Nav() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <nav>
      <Link to="/">FPF</Link>
      <Link to="/jobs">Browse jobs</Link>
      {user?.role === "employer" && (
        <>
          <Link to="/employer">Post a role</Link>
          <Link to="/my-postings">My postings</Link>
        </>
      )}
      {user?.role === "candidate" && <Link to="/my-applications">My applications</Link>}
      {!user && (
        <>
          <Link to="/login">Log in</Link>
          <Link to="/signup">Sign up</Link>
        </>
      )}
      {user && (
        <button onClick={handleLogout} style={{ width: "auto" }}>
          Log out
        </button>
      )}
    </nav>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Nav />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/jobs" element={<BrowseJobs />} />

          <Route
            path="/employer"
            element={
              <ProtectedRoute role="employer">
                <EmployerPost />
              </ProtectedRoute>
            }
          />
          <Route
            path="/my-postings"
            element={
              <ProtectedRoute role="employer">
                <MyPostings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/employer/dashboard/:postingId"
            element={
              <ProtectedRoute role="employer">
                <EmployerDashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/candidate/:postingId"
            element={
              <ProtectedRoute role="candidate">
                <CandidateUpload />
              </ProtectedRoute>
            }
          />
          <Route
            path="/my-applications"
            element={
              <ProtectedRoute role="candidate">
                <MyApplications />
              </ProtectedRoute>
            }
          />
          <Route
            path="/status/:postingId"
            element={
              <ProtectedRoute role="candidate">
                <ApplicationStatusPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
