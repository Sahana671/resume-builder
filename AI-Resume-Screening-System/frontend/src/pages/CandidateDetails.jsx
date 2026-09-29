import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import ScoreCard from "../components/ScoreCard";
import LoadingSpinner from "../components/LoadingSpinner";
import { getCandidate } from "../services/api";
import "../styles/CandidateDetails.css";

export default function CandidateDetails() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCandidate(id)
      .then((res) => setData(res.data))
      .catch((err) => console.error("Failed to load candidate", err))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Navbar />
        <div className="page-content">
          <Link to="/candidates" className="back-link">
            ← Back to Candidates
          </Link>

          {loading ? (
            <LoadingSpinner label="Loading candidate details..." />
          ) : !data ? (
            <p className="empty-state">Candidate not found.</p>
          ) : (
            <>
              <div className="candidate-details-header">
                <div>
                  <h1>{data.candidate.name || "Unnamed Candidate"}</h1>
                  <p className="page-subtitle">{data.candidate.email || "No email extracted"}</p>
                </div>
                {data.resume?.file_name && (
                  <span className="resume-filename">📄 {data.resume.file_name}</span>
                )}
              </div>

              <div className="candidate-details-grid">
                <div className="details-panel">
                  <h3>Candidate Information</h3>
                  <p>
                    <strong>Phone:</strong> {data.resume?.phone || "Not detected"}
                  </p>
                  <p>
                    <strong>Skills:</strong> {data.candidate.skills || "Not specified"}
                  </p>
                  <p>
                    <strong>Experience:</strong> {data.candidate.experience || "Not specified"}
                  </p>
                  <p>
                    <strong>Education:</strong> {data.candidate.education || "Not specified"}
                  </p>
                </div>

                <div className="details-panel">
                  <h3>Screening Results</h3>
                  {data.screening_results.length === 0 ? (
                    <p className="empty-state">This candidate has not been screened against any job yet.</p>
                  ) : (
                    data.screening_results.map((result, idx) => (
                      <div key={idx} className="screening-result-block">
                        <div className="screening-result-header">
                          <ScoreCard score={result.match_score} />
                          <span className={`status-badge status-${result.status.toLowerCase()}`}>
                            {result.status}
                          </span>
                        </div>

                        <div className="sub-scores">
                          <div>
                            <span>Skill Match</span>
                            <div className="mini-bar">
                              <div className="mini-bar-fill" style={{ width: `${result.skill_match_score}%` }} />
                            </div>
                          </div>
                          <div>
                            <span>Experience Match</span>
                            <div className="mini-bar">
                              <div className="mini-bar-fill" style={{ width: `${result.experience_match_score}%` }} />
                            </div>
                          </div>
                          <div>
                            <span>Education Match</span>
                            <div className="mini-bar">
                              <div className="mini-bar-fill" style={{ width: `${result.education_match_score}%` }} />
                            </div>
                          </div>
                          <div>
                            <span>Keyword/JD Match</span>
                            <div className="mini-bar">
                              <div className="mini-bar-fill" style={{ width: `${result.keyword_match_score}%` }} />
                            </div>
                          </div>
                        </div>

                        <p className="ai-summary">
                          <strong>AI Summary:</strong> {result.ai_summary}
                        </p>

                        <p>
                          <strong>✅ Matched Skills:</strong> {result.matched_skills || "None"}
                        </p>
                        <p>
                          <strong>❌ Missing Skills:</strong> {result.missing_skills || "None"}
                        </p>
                      </div>
                    ))
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
