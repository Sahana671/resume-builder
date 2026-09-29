import "../styles/global.css";

/**
 * Simple reusable loading spinner with an optional label.
 */
export default function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="loading-spinner-wrapper">
      <div className="loading-spinner" />
      <p>{label}</p>
    </div>
  );
}
