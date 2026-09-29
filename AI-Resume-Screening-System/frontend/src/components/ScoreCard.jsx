import "../styles/CandidateResults.css";

/**
 * Small circular badge that displays a matching score percentage,
 * colored according to how strong the match is.
 */
export default function ScoreCard({ score }) {
  let colorClass = "score-low";
  if (score >= 80) colorClass = "score-high";
  else if (score >= 50) colorClass = "score-medium";

  return (
    <div className={`score-card ${colorClass}`}>
      <span>{Math.round(score)}%</span>
    </div>
  );
}
