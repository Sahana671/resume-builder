import { useState } from "react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import ResumeUpload from "../components/ResumeUpload";
import "../styles/ResumeUpload.css";

export default function ResumeUploadPage() {
  const [lastResult, setLastResult] = useState(null);

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Navbar />
        <div className="page-content">
          <h1>Upload Resume</h1>
          <p className="page-subtitle">
            Upload a candidate's resume to automatically extract their skills,
            education and experience.
          </p>

          <div className="upload-page-grid">
            <ResumeUpload onUploaded={setLastResult} />

            {lastResult && (
              <div className="extraction-result">
                <h3>Extraction Result</h3>
                <p>
                  <strong>Name:</strong> {lastResult.extracted.name || "Not detected"}
                </p>
                <p>
                  <strong>Email:</strong> {lastResult.extracted.email || "Not detected"}
                </p>
                <p>
                  <strong>Phone:</strong> {lastResult.extracted.phone || "Not detected"}
                </p>
                <p>
                  <strong>Experience:</strong> {lastResult.extracted.experience_years} Years
                </p>
                <p>
                  <strong>Education:</strong>{" "}
                  {lastResult.extracted.education.length
                    ? lastResult.extracted.education.join(", ")
                    : "Not detected"}
                </p>
                <p>
                  <strong>Skills:</strong>{" "}
                  {lastResult.extracted.skills.length
                    ? lastResult.extracted.skills.join(", ")
                    : "Not detected"}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
