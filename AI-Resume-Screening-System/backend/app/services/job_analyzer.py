"""
job_analyzer.py
------------------
Parses a Job Description (JD) to extract required skills, keywords
and requirements so it can later be compared with candidate resumes.
"""

import re
from app.services.skill_extractor import extract_skills, SKILL_VOCABULARY

# Common "filler" words to exclude when extracting keywords from a JD
STOP_WORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "with", "on",
    "is", "are", "be", "as", "at", "by", "this", "that", "will", "we",
    "you", "your", "our", "who", "what", "have", "has", "must", "should",
    "job", "role", "team", "work", "working", "years", "year", "experience",
}


def parse_required_skills(required_skills_text: str) -> list[str]:
    """
    Job forms let recruiters type required skills as a comma-separated
    string (e.g. "Python, SQL, React"). Normalize that into a clean list.
    """
    if not required_skills_text:
        return []
    skills = [s.strip().lower() for s in required_skills_text.split(",")]
    return [s for s in skills if s]


def extract_keywords(description_text: str, top_n: int = 20) -> list[str]:
    """
    Extract the most relevant keywords from the free-text job
    description, using simple frequency counting after removing stop
    words. Also folds in any recognized skills from our vocabulary.
    """
    words = re.findall(r"[a-zA-Z+#.]+", description_text.lower())
    words = [w for w in words if w not in STOP_WORDS and len(w) > 2]

    freq: dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1

    sorted_keywords = sorted(freq.items(), key=lambda item: item[1], reverse=True)
    keywords = [kw for kw, _ in sorted_keywords[:top_n]]

    # Add any vocabulary skills mentioned in the description too
    keywords += extract_skills(description_text)

    return sorted(set(keywords))


def analyze_job(job_title: str, description: str, required_skills_text: str,
                 required_experience: str, required_qualification: str) -> dict:
    """
    Main entry point used by the routes: produces a structured
    representation of a job's requirements for later matching.
    """
    required_skills = parse_required_skills(required_skills_text)
    keywords = extract_keywords(description)

    # Try to parse a numeric years-of-experience requirement, e.g. "2 Years"
    exp_match = re.search(r"(\d+(?:\.\d+)?)", required_experience or "")
    required_years = float(exp_match.group(1)) if exp_match else 0.0

    return {
        "title": job_title,
        "required_skills": required_skills,
        "keywords": keywords,
        "required_years": required_years,
        "required_qualification": (required_qualification or "").lower(),
    }
