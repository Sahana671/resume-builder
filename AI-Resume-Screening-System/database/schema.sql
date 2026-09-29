-- ==========================================================
-- AI Resume Screening System - Database Schema (MySQL)
-- ==========================================================
-- Run this file to create the database and tables:
--   mysql -u root -p < database/schema.sql
--
-- Note: The FastAPI backend can also auto-create these tables
-- via SQLAlchemy on first run. This file is provided so the
-- schema is explicit and reviewable, and for manual setup.
-- ==========================================================

CREATE DATABASE IF NOT EXISTS ai_resume_screening
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ai_resume_screening;

-- ----------------------------------------------------------
-- users: recruiters/admins who log in to the system
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'recruiter',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------
-- jobs: job descriptions created by recruiters
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT NOT NULL,
    required_experience VARCHAR(50),
    required_qualification VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------
-- resumes: uploaded resume files and extracted raw data
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    candidate_name VARCHAR(150),
    candidate_email VARCHAR(150),
    candidate_phone VARCHAR(50),
    raw_text LONGTEXT,
    extracted_skills TEXT,
    extracted_education TEXT,
    extracted_experience TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------
-- candidates: one row per resume, used for listing/ranking
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT NOT NULL,
    name VARCHAR(150),
    email VARCHAR(150),
    skills TEXT,
    experience VARCHAR(100),
    education VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------
-- skills: optional reference table of known/curated skills
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(100)
);

-- ----------------------------------------------------------
-- screening_results: matching score of a candidate for a job
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS screening_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    job_id INT NOT NULL,
    match_score FLOAT DEFAULT 0,
    skill_match_score FLOAT DEFAULT 0,
    experience_match_score FLOAT DEFAULT 0,
    education_match_score FLOAT DEFAULT 0,
    keyword_match_score FLOAT DEFAULT 0,
    matched_skills TEXT,
    missing_skills TEXT,
    ai_summary TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- ==========================================================
-- SAMPLE / DEMO DATA
-- (clearly separate from real uploaded data — safe to delete)
-- ==========================================================

INSERT INTO users (full_name, email, hashed_password, role) VALUES
('Demo Recruiter', 'demo@airesume.com', '$2b$12$KIXQ9G9G9G9G9G9G9G9G9uZQ9G9G9G9G9G9G9G9G9G9G9G9G9G9G', 'recruiter');
-- NOTE: Replace the hashed_password above by registering via /api/auth/register,
-- which correctly bcrypt-hashes a real password. This row is a placeholder.

INSERT INTO jobs (title, description, required_skills, required_experience, required_qualification) VALUES
('Frontend Developer',
 'We are looking for a Frontend Developer skilled in React and modern JavaScript to build responsive, user-friendly web applications.',
 'javascript, react, html, css, git',
 '2 Years',
 'BCA'),
('Backend Developer (Python)',
 'Seeking a Backend Developer experienced with Python, FastAPI and MySQL to design and maintain REST APIs.',
 'python, fastapi, sql, mysql, rest api',
 '1 Years',
 'BCA');

-- Sample demo data for resumes/candidates/screening_results is intentionally
-- left to be generated by actually uploading resumes through the app, so
-- extracted text and matching scores reflect real parsing logic.
