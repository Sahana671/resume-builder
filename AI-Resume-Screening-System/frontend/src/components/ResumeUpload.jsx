import { useState, useRef } from "react";
import { uploadResume } from "../services/api";
import LoadingSpinner from "./LoadingSpinner";
import "../styles/ResumeUpload.css";

/**
 * Reusable drag-and-drop / browse resume uploader.
 * Calls onUploaded(result) once the backend finishes processing the file.
 */
export default function ResumeUpload({ onUploaded }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState(null); // { type: 'success' | 'error', text }
  const inputRef = useRef(null);

  const allowedTypes = [".pdf", ".doc", ".docx"];

  const validateAndSetFile = (file) => {
    if (!file) return;
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!allowedTypes.includes(ext)) {
      setMessage({ type: "error", text: "Only PDF, DOC and DOCX files are allowed." });
      return;
    }
    setSelectedFile(file);
    setMessage(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    validateAndSetFile(e.dataTransfer.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setProgress(0);
    setMessage(null);

    try {
      const response = await uploadResume(selectedFile, (evt) => {
        setProgress(Math.round((evt.loaded * 100) / evt.total));
      });
      setMessage({ type: "success", text: "Resume uploaded and processed successfully!" });
      setSelectedFile(null);
      if (onUploaded) onUploaded(response.data);
    } catch (err) {
      setMessage({
        type: "error",
        text: err.response?.data?.detail || "Upload failed. Please try again.",
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="resume-upload">
      <div
        className={`dropzone ${isDragging ? "dropzone-active" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
      >
        <div className="dropzone-icon">📄</div>
        <p className="dropzone-text">
          Drag &amp; drop a resume here, or <span className="dropzone-link">browse</span>
        </p>
        <p className="dropzone-hint">Supported formats: PDF, DOC, DOCX</p>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.doc,.docx"
          hidden
          onChange={(e) => validateAndSetFile(e.target.files[0])}
        />
      </div>

      {selectedFile && (
        <div className="selected-file">
          <span>📎 {selectedFile.name}</span>
          <button className="btn btn-primary" onClick={handleUpload} disabled={isUploading}>
            {isUploading ? "Uploading..." : "Upload Resume"}
          </button>
        </div>
      )}

      {isUploading && (
        <div className="progress-bar-wrapper">
          <div className="progress-bar" style={{ width: `${progress}%` }} />
          <span className="progress-label">{progress}%</span>
        </div>
      )}

      {isUploading && <LoadingSpinner label="Extracting text and analyzing resume..." />}

      {message && (
        <div className={`alert alert-${message.type}`}>{message.text}</div>
      )}
    </div>
  );
}
