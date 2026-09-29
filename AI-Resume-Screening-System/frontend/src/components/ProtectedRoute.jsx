import { Navigate } from "react-router-dom";

/**
 * Wraps a page element and redirects to /login if there is no
 * auth token stored, protecting dashboard-related pages.
 */
export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}
