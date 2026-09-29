import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import LoadingSpinner from "../components/LoadingSpinner";
import { getResumes, getJobs, getCandidates } from "../services/api";
import "../styles/Dashboard.css";

export default function Dashboard() {
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [resumesRes, jobsRes, candidatesRes] = await Promise.all([
          getResumes(),
          getJobs(),
          getCandidates(),
        ]);
        setResumes(resumesRes.data);
        setJobs(jobsRes.data);
        setCandidates(candidatesRes.data);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const shortlisted = candidates.filter((c) => c.status === "Shortlisted");
  const screened = candidates.filter((c) => c.match_score !== null && c.match_score !== undefined);
  const avgScore =
    screened.length > 0
      ? (screened.reduce((sum, c) => sum + c.match_score, 0) / screened.length).toFixed(1)
      : 0;

  const topCandidates = [...screened]
    .sort((a, b) => (b.match_score || 0) - (a.match_score || 0))
    .slice(0, 5);

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Navbar />
        <div className="page-content">
          <h1>Dashboard</h1>
          <p className="page-subtitle">Overview of your resume screening activity.</p>

          {loading ? (
            <LoadingSpinner label="Loading dashboard..." />
          ) : (
            <>
              <div className="stats-grid">
                <div className="stat-card">
                  <span className="stat-value">{resumes.length}</span>
                  <span className="stat-label">Total Resumes</span>
                </div>
                <div className="stat-card">
                  <span className="stat-value">{jobs.length}</span>
                  <span className="stat-label">Total Jobs</span>
                </div>
                <div className="stat-card">
                  <span className="stat-value">{screened.length}</span>
                  <span className="stat-label">Candidates Screened</span>
                </div>
                <div className="stat-card">
                  <span className="stat-value">{shortlisted.length}</span>
                  <span className="stat-label">Shortlisted Candidates</span>
                </div>
                <div className="stat-card">
                  <span className="stat-value">{avgScore}%</span>
                  <span className="stat-label">Average Matching Score</span>
                </div>
              </div>

              <div className="dashboard-quick-actions">
                <Link to="/resume-upload" className="btn btn-primary">
                  + Upload Resume
                </Link>
                <Link to="/jobs" className="btn btn-outline">
                  + Create Job
                </Link>
                <Link to="/ranking" className="btn btn-outline">
                  View Rankings
                </Link>
              </div>

              <div className="dashboard-grid">
                <div className="dashboard-panel">
                  <h3>Recent Resumes</h3>
                  {resumes.length === 0 ? (
                    <p className="empty-state">No resumes uploaded yet.</p>
                  ) : (
                    <ul className="simple-list">
                      {resumes.slice(0, 5).map((r) => (
                        <li key={r.id}>
                          <strong>{r.candidate_name || r.file_name}</strong>
                          <span>{r.candidate_email || "—"}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <div className="dashboard-panel">
                  <h3>Recent Job Descriptions</h3>
                  {jobs.length === 0 ? (
                    <p className="empty-state">No job descriptions created yet.</p>
                  ) : (
                    <ul className="simple-list">
                      {jobs.slice(0, 5).map((j) => (
                        <li key={j.id}>
                          <strong>{j.title}</strong>
                          <span>{j.required_experience || "Any experience"}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <div className="dashboard-panel">
                  <h3>Top Candidates</h3>
                  {topCandidates.length === 0 ? (
                    <p className="empty-state">No candidates screened yet.</p>
                  ) : (
                    <ul className="simple-list">
                      {topCandidates.map((c) => (
                        <li key={c.id}>
                          <strong>{c.name || "Unnamed"}</strong>
                          <span>{Math.round(c.match_score)}%</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
