import { NavLink } from "react-router-dom";
import "../styles/global.css";

/**
 * Left-hand sidebar navigation used inside the authenticated
 * (dashboard) area of the app.
 */
const links = [
  { to: "/dashboard", label: "Dashboard", icon: "📊" },
  { to: "/resume-upload", label: "Upload Resume", icon: "📄" },
  { to: "/jobs", label: "Job Descriptions", icon: "💼" },
  { to: "/candidates", label: "Candidates", icon: "👥" },
  { to: "/ranking", label: "Ranking", icon: "🏆" },
  { to: "/profile", label: "Profile", icon: "⚙️" },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">AI Screening</div>
      <ul className="sidebar-list">
        {links.map((link) => (
          <li key={link.to}>
            <NavLink
              to={link.to}
              className={({ isActive }) =>
                isActive ? "sidebar-link active" : "sidebar-link"
              }
            >
              <span className="sidebar-icon">{link.icon}</span>
              {link.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </aside>
  );
}
