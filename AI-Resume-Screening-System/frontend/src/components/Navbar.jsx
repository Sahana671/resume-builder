import { Link, useNavigate } from "react-router-dom";
import "../styles/global.css";

/**
 * Top navigation bar shown across the app (public + authenticated pages).
 */
export default function Navbar() {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem("token");

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <span className="brand-icon">🤖</span>
        AI Resume Screening
      </Link>

      <div className="navbar-links">
        {isLoggedIn ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/jobs">Jobs</Link>
            <Link to="/candidates">Candidates</Link>
            <Link to="/profile">Profile</Link>
            <button className="btn btn-outline" onClick={handleLogout}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register" className="btn btn-primary">
              Get Started
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
