import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import CandidateCard from "../components/CandidateCard";
import LoadingSpinner from "../components/LoadingSpinner";
import { getCandidates } from "../services/api";
import "../styles/CandidateResults.css";

export default function CandidateResults() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("All");

  useEffect(() => {
    getCandidates()
      .then((res) => setCandidates(res.data))
      .catch((err) => console.error("Failed to load candidates", err))
      .finally(() => setLoading(false));
  }, []);

  const filtered =
    statusFilter === "All" ? candidates : candidates.filter((c) => c.status === statusFilter);

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Navbar />
        <div className="page-content">
          <h1>Candidate Results</h1>
          <p className="page-subtitle">All candidates extracted from uploaded resumes.</p>

          <div className="filter-row">
            {["All", "Shortlisted", "Pending", "Rejected", "Not Screened"].map((status) => (
              <button
                key={status}
                className={`filter-chip ${statusFilter === status ? "active" : ""}`}
                onClick={() => setStatusFilter(status)}
              >
                {status}
              </button>
            ))}
          </div>

          {loading ? (
            <LoadingSpinner label="Loading candidates..." />
          ) : filtered.length === 0 ? (
            <p className="empty-state">No candidates found. Upload resumes to get started.</p>
          ) : (
            <div className="candidate-grid">
              {filtered.map((candidate) => (
                <CandidateCard key={candidate.id} candidate={candidate} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
