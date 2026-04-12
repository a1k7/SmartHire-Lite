import re
from typing import List, Tuple
import pdfplumber

# ==============================
# 🔥 JOB ROLE SKILL MAP
# ==============================

JOB_ROLE_SKILLS = {
    "vessel supervisor": [
        "port operations", "vessel coordination", "cargo handling",
        "marine safety", "terminal operations", "logistics coordination"
    ],
    "vessel foreman": [
        "crew supervision", "dock operations", "loading unloading",
        "shift management", "equipment handling"
    ],
    "document controller": [
        "documentation", "record management", "data entry",
        "ms excel", "compliance", "filing systems"
    ],
    "cargo delivery clerk": [
        "inventory management", "dispatch", "logistics",
        "delivery coordination", "warehouse"
    ],
    "gate clerk": [
        "entry management", "security checks", "data logging",
        "access control", "gate operations"
    ],
    "mooring gang": [
        "rope handling", "vessel docking", "marine operations",
        "physical labor", "team coordination"
    ],
    "custom foreman": [
        "customs clearance", "import export", "documentation",
        "compliance", "cargo inspection"
    ],
    "service administrator": [
        "administration", "customer service", "reporting",
        "coordination", "office operations"
    ]
}

# ==============================
# LOCATION + QID
# ==============================

LOCATION_KEYWORDS = ["qatar", "doha", "gcc", "middle east"]
QID_KEYWORDS = ["qid", "qatar id", "resident permit", "valid qid"]

# ==============================
# SKILLS DB
# ==============================

SKILL_DB = {
    "business": ["management", "operations", "logistics", "coordination"],
    "tools": ["excel", "word", "sap", "erp"]
}

EXPANDED_SKILLS = []

for category in SKILL_DB.values():
    for skill in category:
        EXPANDED_SKILLS.extend([
            skill,
            skill.replace(" ", ""),
            skill.replace(" ", "-"),
            skill + " experience"
        ])

ALL_SKILLS = sorted(set(EXPANDED_SKILLS))

SKILL_PATTERNS = {
    skill: re.compile(r"\b" + re.escape(skill) + r"\b")
    for skill in ALL_SKILLS
}

# ==============================
# 🔥 MISSING FUNCTION FIX
# ==============================

def normalize_filename(name: str) -> str:
    name = re.sub(r"\.pdf$", "", name, flags=re.IGNORECASE)
    name = name.replace("-", " ").replace("_", " ")
    return re.sub(r"\s+", " ", name).title().strip()

# ==============================
# PDF EXTRACTION
# ==============================

def extract_text_from_pdf(file) -> str:
    text = ""
    try:
        if hasattr(file, "seek"):
            file.seek(0)
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += "\n" + (page.extract_text() or "")
    except:
        return ""
    return text.lower().strip()

# ==============================
# CLEAN TEXT
# ==============================

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

# ==============================
# SKILL EXTRACTION
# ==============================

def extract_skills(text: str) -> List[str]:
    cleaned = clean_text(text)
    found = []

    for skill, pattern in SKILL_PATTERNS.items():
        if pattern.search(cleaned):
            found.append(skill)

    return sorted(set(found))

# ==============================
# ROLE DETECTION
# ==============================

def detect_role(job_text: str) -> str:
    job_text = job_text.lower()
    for role in JOB_ROLE_SKILLS.keys():
        if role in job_text:
            return role
    return "general"

# ==============================
# QATAR DETECTION
# ==============================

def detect_qatar_status(text: str) -> Tuple[bool, bool]:
    text = text.lower()
    in_qatar = any(k in text for k in LOCATION_KEYWORDS)
    has_qid = any(k in text for k in QID_KEYWORDS)
    return in_qatar, has_qid

# ==============================
# SCORING
# ==============================

def score_resume(job_text: str, resume_text: str, semantic_score: float):

    job_text = clean_text(job_text)
    resume_text = clean_text(resume_text)

    job_skills = extract_skills(job_text)
    resume_skills = extract_skills(resume_text)

    matched = sorted(set(job_skills) & set(resume_skills))
    missing = sorted(set(job_skills) - set(resume_skills))

    skill_ratio = len(matched) / len(job_skills) if job_skills else 0

    role = detect_role(job_text)
    role_skills = JOB_ROLE_SKILLS.get(role, [])

    role_match_count = sum(1 for skill in role_skills if skill in resume_text)
    role_score = role_match_count / len(role_skills) if role_skills else 0

    in_qatar, has_qid = detect_qatar_status(resume_text)

    location_bonus = 0
    if in_qatar:
        location_bonus += 0.1
    if has_qid:
        location_bonus += 0.1

    final_score = round(
        ((0.5 * semantic_score) +
         (0.3 * skill_ratio) +
         (0.2 * role_score) +
         location_bonus) * 100, 2
    )

    return final_score, matched, missing, role, in_qatar, has_qid

# ==============================
# AI SUMMARY
# ==============================

def generate_ai_summary(name, score, matched, missing, role, in_qatar, has_qid):

    if score >= 85:
        level = "highly suitable"
    elif score >= 70:
        level = "strong fit"
    elif score >= 50:
        level = "moderate fit"
    else:
        level = "low alignment"

    if in_qatar and has_qid:
        location_note = "Candidate is locally available in Qatar with QID ✅"
    elif in_qatar:
        location_note = "Candidate is in Qatar but QID unclear ⚠"
    else:
        location_note = "Candidate not clearly based in Qatar ❌"

    return f"""
{name} appears to be a {level} candidate for the role: {role}.

✔ Strengths: {", ".join(matched[:5]) if matched else "Limited overlap"}

⚠ Gaps: {", ".join(missing[:5]) if missing else "No major gaps"}

📍 {location_note}

This profile shows {level} alignment with job requirements.
""".strip()
