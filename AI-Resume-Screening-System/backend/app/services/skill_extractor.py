"""
skill_extractor.py
--------------------
Extracts skills, education and experience information from resume
text using a keyword/pattern based approach.

This is a deliberately simple, explainable "NLP" implementation
suited for a final-year project. It can later be replaced with a
trained NER model (spaCy, transformers) — the rest of the system
only depends on the function signatures below, not the internal
implementation.
"""

import re

# A reference skill vocabulary. In a real product this would live in
# the database or a much larger curated list / embeddings model.
SKILL_VOCABULARY = [
    "python", "java", "javascript", "typescript", "c++", "c#", "c",
    "html", "css", "react", "react.js", "angular", "vue", "node.js", "node",
    "express", "django", "flask", "fastapi", "spring", "spring boot",
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "linux",
    "machine learning", "deep learning", "nlp", "data science",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "rest api", "graphql", "microservices", "agile", "scrum",
    "excel", "power bi", "tableau", "communication", "leadership",
    "project management", "problem solving", "teamwork",
]

EDUCATION_KEYWORDS = [
    "b.tech", "btech", "bachelor of technology",
    "bca", "bachelor of computer applications",
    "mca", "master of computer applications",
    "b.sc", "bsc", "bachelor of science",
    "m.sc", "msc", "master of science",
    "mba", "master of business administration",
    "b.e", "be", "bachelor of engineering",
    "m.tech", "mtech", "master of technology",
    "phd", "diploma", "high school", "12th", "10th",
]


def extract_skills(text: str) -> list[str]:
    """
    Scan resume text for known skill keywords (case-insensitive,
    whole-word / whole-phrase match) and return the matches found.
    """
    text_lower = text.lower()
    found_skills = []

    for skill in SKILL_VOCABULARY:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return sorted(set(found_skills))


def extract_education(text: str) -> list[str]:
    """Scan resume text for education-related keywords."""
    text_lower = text.lower()
    found = [kw for kw in EDUCATION_KEYWORDS if kw in text_lower]
    return sorted(set(found))


def extract_experience_years(text: str) -> float:
    """
    Attempt to find a stated number of years of experience in the
    resume, e.g. "3 years of experience" or "2+ years".
    Returns 0 if nothing is found.
    """
    match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", text.lower())
    if match:
        return float(match.group(1))
    return 0.0


def analyze_resume_skills(raw_text: str) -> dict:
    """
    Convenience wrapper used by the routes to get all extracted
    information from a resume in one call.
    """
    return {
        "skills": extract_skills(raw_text),
        "education": extract_education(raw_text),
        "experience_years": extract_experience_years(raw_text),
    }
