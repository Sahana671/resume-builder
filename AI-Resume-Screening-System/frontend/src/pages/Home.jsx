import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import "../styles/Home.css";

export default function Home() {
  return (
    <div className="home-page">
      <Navbar />

      {/* Hero Section */}
      <section className="hero">
        <h1>AI Resume Screening System</h1>
        <p>
          Automatically analyze, match and rank candidate resumes against job
          descriptions using NLP-powered scoring — saving recruiters hours of
          manual screening.
        </p>
        <Link to="/register" className="btn btn-primary btn-lg">
          Get Started
        </Link>
      </section>

      {/* Features Section */}
      <section className="section">
        <h2>Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📄</div>
            <h3>Smart Resume Parsing</h3>
            <p>Extracts skills, education, experience and contact details from PDF/DOCX resumes.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🧠</div>
            <h3>NLP-Based Matching</h3>
            <p>Compares resumes against job descriptions using explainable keyword and skill matching.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Matching Score</h3>
            <p>Generates a weighted candidate matching score across skills, experience and education.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🏆</div>
            <h3>Candidate Ranking</h3>
            <p>Automatically ranks and shortlists the best-fit candidates for every job opening.</p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="section section-alt">
        <h2>How It Works</h2>
        <div className="steps-grid">
          <div className="step-card">
            <span className="step-number">1</span>
            <h4>Create a Job Description</h4>
            <p>Enter the role, required skills, experience and qualification.</p>
          </div>
          <div className="step-card">
            <span className="step-number">2</span>
            <h4>Upload Resumes</h4>
            <p>Drag and drop candidate resumes in PDF or DOCX format.</p>
          </div>
          <div className="step-card">
            <span className="step-number">3</span>
            <h4>AI Analyzes &amp; Scores</h4>
            <p>The NLP engine extracts data and calculates a matching score.</p>
          </div>
          <div className="step-card">
            <span className="step-number">4</span>
            <h4>Review Rankings</h4>
            <p>View ranked, shortlisted candidates ready for interview.</p>
          </div>
        </div>
      </section>

      {/* AI/NLP Explanation */}
      <section className="section">
        <h2>The AI/NLP Behind the Scores</h2>
        <p className="section-text">
          Each resume is scored using a transparent, weighted formula: 50%
          skill match, 20% experience match, 15% education match, and 15%
          keyword/JD match. This keeps the scoring explainable while still
          being modular enough to later swap in a more advanced machine
          learning model.
        </p>
      </section>

      <footer className="footer">
        <p>© {new Date().getFullYear()} AI Resume Screening System — Final Year Project</p>
      </footer>
    </div>
  );
}
