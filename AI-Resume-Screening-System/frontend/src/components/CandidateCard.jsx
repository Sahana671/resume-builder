import { Link } from "react-router-dom";
import ScoreCard from "./ScoreCard";
import "../styles/CandidateResults.css";

/**
 * Card summarizing a single candidate in the Candidate Results page.
 */
export default function CandidateCard({ candidate }) {
  const statusClass =
    candidate.status === "Shortlisted"
      ? "status-shortlisted"
      : candidate.status === "Rejected"
      ? "status-rejected"
      : "status-pending";

  return (
    <div className="candidate-card">
      <div className="candidate-card-header">
        <div>
          <h3>{candidate.name || "Unnamed Candidate"}</h3>
          <p className="candidate-email">{candidate.email || "No email extracted"}</p>
        </div>
        {candidate.match_score !== null && candidate.match_score !== undefined && (
          <ScoreCard score={candidate.match_score} />
        )}
      </div>

      <div className="candidate-card-body">
        <p>
          <strong>Skills:</strong> {candidate.skills || "Not specified"}
        </p>
        <p>
          <strong>Experience:</strong> {candidate.experience || "Not specified"}
        </p>
        <p>
          <strong>Education:</strong> {candidate.education || "Not specified"}
        </p>
      </div>

      <div className="candidate-card-footer">
        <span className={`status-badge ${statusClass}`}>{candidate.status}</span>
        <Link to={`/candidates/${candidate.id}`} className="btn btn-outline">
          View Details
        </Link>
      </div>
    </div>
  );
}
