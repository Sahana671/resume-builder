import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import JobDescriptionForm from "../components/JobDescriptionForm";
import LoadingSpinner from "../components/LoadingSpinner";
import { getJobs, getResumes, analyzeScreening } from "../services/api";
import "../styles/JobDescription.css";

export default function JobDescription() {
  const [jobs, setJobs] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [screeningJobId, setScreeningJobId] = useState(null);
  const [screeningMessage, setScreeningMessage] = useState(null);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const [jobsRes, resumesRes] = await Promise.all([getJobs(), getResumes()]);
      setJobs(jobsRes.data);
      setResumes(resumesRes.data);
    } catch (err) {
      console.error("Failed to load jobs", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const handleScreenAll = async (jobId) => {
    setScreeningJobId(jobId);
    setScreeningMessage(null);
    try {
      for (const resume of resumes) {
        await analyzeScreening(resume.id, jobId);
      }
      setScreeningMessage({
        type: "success",
        text: `Screened ${resumes.length} resume(s) against this job. Check the Candidates or Ranking page.`,
      });
    } catch (err) {
      setScreeningMessage({ type: "error", text: "Screening failed. Please try again." });
    } finally {
      setScreeningJobId(null);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <Navbar />
        <div className="page-content">
          <h1>Job Descriptions</h1>
          <p className="page-subtitle">Create job postings and run AI screening against uploaded resumes.</p>

          {screeningMessage && (
            <div className={`alert alert-${screeningMessage.type}`}>{screeningMessage.text}</div>
          )}

          <div className="jd-page-grid">
            <div className="jd-form-panel">
              <h3>Create New Job</h3>
              <JobDescriptionForm onCreated={loadJobs} />
            </div>

            <div className="jd-list-panel">
              <h3>Existing Jobs</h3>
              {loading ? (
                <LoadingSpinner label="Loading jobs..." />
              ) : jobs.length === 0 ? (
                <p className="empty-state">No jobs created yet. Add one to get started.</p>
              ) : (
                <div className="jd-list">
                  {jobs.map((job) => (
                    <div key={job.id} className="jd-item">
                      <div className="jd-item-header">
                        <h4>{job.title}</h4>
                        <span className="jd-item-exp">{job.required_experience || "Any experience"}</span>
                      </div>
                      <p className="jd-item-desc">{job.description}</p>
                      <p className="jd-item-skills">
                        <strong>Skills:</strong> {job.required_skills}
                      </p>
                      <div className="jd-item-actions">
                        <button
                          className="btn btn-primary"
                          disabled={screeningJobId === job.id || resumes.length === 0}
                          onClick={() => handleScreenAll(job.id)}
                        >
                          {screeningJobId === job.id ? "Screening..." : "Run AI Screening"}
                        </button>
                        <Link to="/ranking" className="btn btn-outline">
                          View Ranking
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
