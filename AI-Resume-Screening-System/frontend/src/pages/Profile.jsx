import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import "../styles/Profile.css";

export default function Profile() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "null");

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Navbar />
        <div className="page-content">
          <h1>Profile</h1>
          <p className="page-subtitle">Your account information.</p>

          <div className="profile-card">
            <div className="profile-avatar">
              {(user?.full_name || "U").charAt(0).toUpperCase()}
            </div>
            <h2>{user?.full_name || "Unknown User"}</h2>
            <p className="profile-email">{user?.email || "—"}</p>

            <div className="profile-info-grid">
              <div>
                <span className="profile-label">Role</span>
                <span className="profile-value">{user?.role || "recruiter"}</span>
              </div>
              <div>
                <span className="profile-label">Account ID</span>
                <span className="profile-value">#{user?.id ?? "—"}</span>
              </div>
            </div>

            <button className="btn btn-outline btn-block" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
