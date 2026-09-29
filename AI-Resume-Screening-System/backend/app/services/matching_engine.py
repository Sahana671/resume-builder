"""
matching_engine.py
---------------------
The heart of the AI Resume Screening System.

Compares an extracted resume (skills, education, experience, raw
text) against an analyzed job description and produces:

  - skill match score
  - experience match score
  - education match score
  - keyword/JD match score
  - a final weighted matching score
  - the list of matched skills
  - the list of missing skills
  - a short AI-style summary

The weighting scheme (kept deliberately simple and explainable):

    Skill Match      = 50%
    Experience Match = 20%
    Education Match  = 15%
    Keyword/JD Match = 15%

This module is intentionally rule-based/explainable rather than a
black-box ML model, which suits a final-year academic project. It is
written so the scoring function could later be swapped out for a
trained ML/embeddings-based model without changing the API contract.
"""

WEIGHTS = {
    "skill": 0.50,
    "experience": 0.20,
    "education": 0.15,
    "keyword": 0.15,
}


def _skill_match(resume_skills: list[str], required_skills: list[str]) -> tuple[float, list[str], list[str]]:
    """Compare resume skills to required skills and score 0-100."""
    if not required_skills:
        return 100.0, resume_skills, []

    resume_skills_set = set(s.lower() for s in resume_skills)
    required_set = set(s.lower() for s in required_skills)

    matched = sorted(resume_skills_set & required_set)
    missing = sorted(required_set - resume_skills_set)

    score = (len(matched) / len(required_set)) * 100 if required_set else 100.0
    return round(score, 2), matched, missing


def _experience_match(resume_years: float, required_years: float) -> float:
    """Score 0-100 based on how resume experience compares to requirement."""
    if required_years <= 0:
        return 100.0
    if resume_years >= required_years:
        return 100.0
    return round((resume_years / required_years) * 100, 2)


def _education_match(resume_education: list[str], required_qualification: str) -> float:
    """Score 0-100 based on whether the required qualification appears in resume education."""
    if not required_qualification:
        return 100.0

    required_qualification = required_qualification.lower()
    for edu in resume_education:
        if edu.lower() in required_qualification or required_qualification in edu.lower():
            return 100.0
    return 40.0 if resume_education else 0.0


def _keyword_match(resume_text: str, keywords: list[str]) -> float:
    """Score 0-100 based on the percentage of JD keywords present in the resume text."""
    if not keywords:
        return 100.0

    text_lower = resume_text.lower()
    found = sum(1 for kw in keywords if kw in text_lower)
    return round((found / len(keywords)) * 100, 2)


def generate_summary(candidate_name: str, final_score: float, matched: list[str], missing: list[str]) -> str:
    """Produce a short, human-readable AI-style summary of the match."""
    name = candidate_name or "This candidate"

    if final_score >= 80:
        verdict = "is a strong match"
    elif final_score >= 60:
        verdict = "is a reasonable match"
    else:
        verdict = "is not a strong match"

    summary = f"{name} {verdict} for this role with a matching score of {final_score}%. "

    if matched:
        summary += f"Matched skills: {', '.join(matched[:8])}. "
    if missing:
        summary += f"Missing skills: {', '.join(missing[:8])}."

    return summary.strip()


def calculate_match(resume_data: dict, job_data: dict) -> dict:
    """
    Main entry point used by the routes.

    resume_data expects: skills (list), education (list),
        experience_years (float), raw_text (str), name (str)
    job_data expects: required_skills (list), required_years (float),
        required_qualification (str), keywords (list)
    """
    skill_score, matched_skills, missing_skills = _skill_match(
        resume_data.get("skills", []), job_data.get("required_skills", [])
    )
    experience_score = _experience_match(
        resume_data.get("experience_years", 0.0), job_data.get("required_years", 0.0)
    )
    education_score = _education_match(
        resume_data.get("education", []), job_data.get("required_qualification", "")
    )
    keyword_score = _keyword_match(
        resume_data.get("raw_text", ""), job_data.get("keywords", [])
    )

    final_score = (
        skill_score * WEIGHTS["skill"]
        + experience_score * WEIGHTS["experience"]
        + education_score * WEIGHTS["education"]
        + keyword_score * WEIGHTS["keyword"]
    )
    final_score = round(final_score, 2)

    status = "Shortlisted" if final_score >= 70 else ("Pending" if final_score >= 40 else "Rejected")

    summary = generate_summary(resume_data.get("name"), final_score, matched_skills, missing_skills)

    return {
        "match_score": final_score,
        "skill_match_score": skill_score,
        "experience_match_score": experience_score,
        "education_match_score": education_score,
        "keyword_match_score": keyword_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "status": status,
        "ai_summary": summary,
    }
