
import re
from typing import List, Tuple

import pdfplumber


SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "react", "node", "flask",
    "django", "fastapi", "sql", "mongodb", "postgresql", "api", "rest",
    "html", "css", "git", "github",
    "photoshop", "illustrator", "adobe illustrator", "adobe photoshop",
    "premiere", "premiere pro", "after effects", "davinci resolve",
    "video editing", "editing", "graphic design", "design", "branding",
    "marketing", "content", "storytelling", "production",
    "communication", "management", "leadership", "operations",
    "analysis", "data analysis", "reporting", "sales",
    "fitness", "nutrition", "logistics", "warehouse"
]


def extract_text_from_pdf(file) -> str:
    """
    Accepts either a Streamlit uploaded file object or a file path.
    Returns extracted lowercase text.
    """
    text = ""

    try:
        if hasattr(file, "seek"):
            file.seek(0)

        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += "\n" + page_text
    except Exception:
        return ""

    return text.lower().strip()


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_filename(name: str) -> str:
    name = re.sub(r"\.pdf$", "", name, flags=re.IGNORECASE)
    name = name.replace("-", " ").replace("_", " ")
    name = re.sub(r"\s+", " ", name).strip()
    return name.title()


def extract_skills(text: str) -> List[str]:
    """
    Returns a flat list of matched skill strings.
    No nested lists.
    """
    cleaned = clean_text(text)
    found = []

    for skill in SKILL_KEYWORDS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, cleaned):
            found.append(skill)

    return sorted(set(found))


def score_resume(job_text: str, resume_text: str, semantic_score: float) -> Tuple[float, List[str], List[str]]:
    """
    Hybrid score:
    - semantic similarity
    - required skill match
    - bonus skill match
    Returns:
      final_score (0-100),
      matched_skills,
      missing_skills
    """
    job_skills = extract_skills(job_text)
    resume_skills = extract_skills(resume_text)

    matched_skills = sorted(set(job_skills).intersection(set(resume_skills)))
    missing_skills = sorted(set(job_skills) - set(resume_skills))

    if job_skills:
        skill_match_ratio = len(matched_skills) / len(job_skills)
    else:
        skill_match_ratio = 0.0

    # Weighted score
    raw_score = (0.55 * semantic_score) + (0.45 * skill_match_ratio)
    final_score = round(raw_score * 100, 2)

    return final_score, matched_skills, missing_skills
def generate_ai_summary(candidate_name, score, matched, missing):
    """
    Generates human-like AI summary without using any API
    """

    if score >= 80:
        level = "highly suitable"
    elif score >= 60:
        level = "a strong potential fit"
    elif score >= 40:
        level = "a moderate fit"
    else:
        level = "not a strong match"

    matched_text = ", ".join(matched[:4]) if matched else "limited relevant skills"
    missing_text = ", ".join(missing[:3]) if missing else "no major skill gaps"

    summary = f"""
{candidate_name} appears to be {level} for this role.

Strengths include: {matched_text}.

Potential gaps: {missing_text}.

Overall, this candidate shows {level} alignment with the job requirements.
"""

    return summary.strip()