/**
 * api.js
 * -------
 * Central Axios instance and API helper functions used across the
 * whole frontend. Every backend call goes through here so the base
 * URL, auth header and error handling stay consistent.
 */

import axios from "axios";

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL;
const API_BASE_URL = rawBaseUrl !== undefined ? rawBaseUrl : "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Attach the JWT token (if present) to every request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ---------- Auth ----------
export const registerUser = (data) => api.post("/api/auth/register", data);
export const loginUser = (data) => api.post("/api/auth/login", data);

// ---------- Resumes ----------
export const uploadResume = (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/api/resumes/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });
};
export const getResumes = () => api.get("/api/resumes");
export const getResume = (id) => api.get(`/api/resumes/${id}`);

// ---------- Jobs ----------
export const createJob = (data) => api.post("/api/jobs", data);
export const getJobs = () => api.get("/api/jobs");
export const getJob = (id) => api.get(`/api/jobs/${id}`);

// ---------- Screening / Candidates ----------
export const analyzeScreening = (resumeId, jobId) =>
  api.post("/api/screening/analyze", { resume_id: resumeId, job_id: jobId });
export const getCandidates = () => api.get("/api/candidates");
export const getCandidate = (id) => api.get(`/api/candidates/${id}`);

// ---------- Ranking ----------
export const getRanking = (jobId) => api.get(`/api/ranking/${jobId}`);

export default api;
