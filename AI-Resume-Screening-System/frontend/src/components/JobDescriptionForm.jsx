import { useState } from "react";
import { createJob } from "../services/api";
import "../styles/JobDescription.css";

/**
 * Form for a recruiter to create a new Job Description.
 * Calls onCreated(job) once the job has been saved.
 */
export default function JobDescriptionForm({ onCreated }) {
  const [form, setForm] = useState({
    title: "",
    description: "",
    required_skills: "",
    required_experience: "",
    required_qualification: "",
  });
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!form.title || !form.description || !form.required_skills) {
      setError("Job title, description and required skills are required.");
      return;
    }

    setSaving(true);
    try {
      const response = await createJob(form);
      setForm({
        title: "",
        description: "",
        required_skills: "",
        required_experience: "",
        required_qualification: "",
      });
      if (onCreated) onCreated(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save job. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className="jd-form" onSubmit={handleSubmit}>
      {error && <div className="alert alert-error">{error}</div>}

      <label>Job Title</label>
      <input
        type="text"
        name="title"
        placeholder="e.g. Frontend Developer"
        value={form.title}
        onChange={handleChange}
      />

      <label>Job Description</label>
      <textarea
        name="description"
        rows={5}
        placeholder="Describe the role, responsibilities and expectations..."
        value={form.description}
        onChange={handleChange}
      />

      <label>Required Skills (comma-separated)</label>
      <input
        type="text"
        name="required_skills"
        placeholder="e.g. Python, SQL, React"
        value={form.required_skills}
        onChange={handleChange}
      />

      <div className="jd-form-row">
        <div>
          <label>Required Experience</label>
          <input
            type="text"
            name="required_experience"
            placeholder="e.g. 2 Years"
            value={form.required_experience}
            onChange={handleChange}
          />
        </div>
        <div>
          <label>Required Qualification</label>
          <input
            type="text"
            name="required_qualification"
            placeholder="e.g. BCA"
            value={form.required_qualification}
            onChange={handleChange}
          />
        </div>
      </div>

      <button type="submit" className="btn btn-primary" disabled={saving}>
        {saving ? "Saving..." : "Save Job"}
      </button>
    </form>
  );
}
