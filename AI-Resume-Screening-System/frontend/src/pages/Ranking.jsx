import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import LoadingSpinner from "../components/LoadingSpinner";
import { getJobs, getRanking } from "../services/api";
import "../styles/Ranking.css";

export default function Ranking() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [ranking, setRanking] = useState(null);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [loadingRanking, setLoadingRanking] = useState(false);

  useEffect(() => {
    getJobs()
      .then((res) => {
        setJobs(res.data);
        if (res.data.length > 0) setSelectedJobId(res.data[0].id);
      })
      .catch((err) => console.error("Failed to load jobs", err))
      .finally(() => setLoadingJobs(false));
  }, []);

  useEffect(() => {
    if (!selectedJobId) return;
    setLoadingRanking(true);
    getRanking(selectedJobId)
      .then((res) => setRanking(res.data))
      .catch((err) => console.error("Failed to load ranking", err))
      .finally(() => setLoadingRanking(false));
  }, [selectedJobId]);

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Navbar />
        <div className="page-content">
          <h1>Candidate Ranking</h1>
          <p className="page-subtitle">Candidates ranked by AI matching score for a selected job.</p>

          {loadingJobs ? (
            <LoadingSpinner label="Loading jobs..." />
          ) : jobs.length === 0 ? (
            <p className="empty-state">No jobs available. Create a job first.</p>
          ) : (
            <>
              <div className="ranking-job-select">
                <label>Select Job:</label>
                <select value={selectedJobId} onChange={(e) => setSelectedJobId(e.target.value)}>
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.title}
                    </option>
                  ))}
                </select>
              </div>

              {loadingRanking ? (
                <LoadingSpinner label="Loading ranking..." />
              ) : !ranking || ranking.ranking.length === 0 ? (
                <p className="empty-state">
                  No candidates have been screened against this job yet. Go to the Job Descriptions page
                  and run AI Screening.
                </p>
              ) : (
                <div className="ranking-list">
                  {ranking.ranking.map((entry) => (
                    <Link
                      to={`/candidates/${entry.candidate_id}`}
                      key={entry.candidate_id}
                      className="ranking-row"
                    >
                      <span className="ranking-position">#{entry.rank}</span>
                      <span className="ranking-name">{entry.name}</span>
                      <div className="ranking-bar-wrapper">
                        <div className="ranking-bar" style={{ width: `${entry.match_score}%` }} />
                      </div>
                      <span className="ranking-score">{Math.round(entry.match_score)}%</span>
                      <span className={`status-badge status-${entry.status.toLowerCase()}`}>
                        {entry.status}
                      </span>
                    </Link>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
