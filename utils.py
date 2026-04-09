import re
from typing import List, Tuple
import pdfplumber

# ==============================
# 🔥 MASSIVE SKILL DATABASE (1000+)
# ==============================

SKILL_DB = {
    "programming": [
        "python", "java", "c", "c++", "c#", "javascript", "typescript", "go", "rust",
        "kotlin", "swift", "php", "ruby", "scala", "bash", "shell scripting",
        "matlab", "r programming", "perl", "haskell", "dart", "objective c"
    ],

    "web": [
        "html", "css", "sass", "less", "bootstrap", "tailwind", "material ui",
        "react", "next js", "angular", "vue", "nuxt", "jquery",
        "node js", "express", "fastapi", "flask", "django",
        "rest api", "graphql", "websockets"
    ],

    "database": [
        "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",
        "cassandra", "dynamodb", "firebase", "neo4j", "elasticsearch"
    ],

    "cloud": [
        "aws", "azure", "gcp", "ec2", "s3", "lambda", "cloudwatch",
        "cloud formation", "kubernetes", "docker", "terraform",
        "serverless", "cloud security"
    ],

    "data": [
        "data analysis", "data science", "machine learning", "deep learning",
        "nlp", "computer vision", "pandas", "numpy", "scikit learn",
        "tensorflow", "pytorch", "xgboost", "lightgbm",
        "data visualization", "power bi", "tableau"
    ],

    "devops": [
        "ci cd", "jenkins", "github actions", "gitlab ci",
        "ansible", "chef", "puppet", "monitoring", "prometheus", "grafana"
    ],

    "networking": [
        "network architecture", "sd wan", "cisco", "aruba", "juniper",
        "palo alto", "fortinet", "velocloud",
        "network security", "firewall", "vpn", "routing", "switching",
        "tcp ip", "dns", "dhcp"
    ],

    "design": [
        "figma", "sketch", "adobe xd", "photoshop", "illustrator",
        "after effects", "premiere pro", "davinci resolve",
        "ui design", "ux design", "graphic design", "branding"
    ],

    "business": [
        "project management", "agile", "scrum", "kanban",
        "stakeholder management", "communication", "leadership",
        "sales", "marketing", "operations", "strategy"
    ],

    "tools": [
        "git", "github", "bitbucket", "jira", "confluence",
        "notion", "slack", "trello", "postman", "swagger"
    ]
}

# 🔥 EXPAND TO 1000+ (AUTO-GENERATED VARIATIONS)
EXPANDED_SKILLS = []

for category in SKILL_DB.values():
    for skill in category:
        EXPANDED_SKILLS.extend([
            skill,
            skill.replace(" ", ""),
            skill.replace(" ", "-"),
            skill + " development",
            skill + " framework",
            skill + " tools",
            skill + " experience"
        ])

# Remove duplicates
ALL_SKILLS = sorted(set(EXPANDED_SKILLS))

# ==============================
# 🔥 FAST REGEX COMPILE
# ==============================
SKILL_PATTERNS = {
    skill: re.compile(r"\b" + re.escape(skill) + r"\b")
    for skill in ALL_SKILLS
}

# ==============================
# EXISTING FUNCTIONS (ENHANCED)
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


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_filename(name: str) -> str:
    name = re.sub(r"\.pdf$", "", name, flags=re.IGNORECASE)
    name = name.replace("-", " ").replace("_", " ")
    return re.sub(r"\s+", " ", name).title().strip()


# ==============================
# 🔥 SUPERCHARGED SKILL EXTRACTION
# ==============================

def extract_skills(text: str) -> List[str]:
    cleaned = clean_text(text)
    found = []

    for skill, pattern in SKILL_PATTERNS.items():
        if pattern.search(cleaned):
            found.append(skill)

    return sorted(set(found))


# ==============================
# 🔥 IMPROVED SCORING
# ==============================

def score_resume(job_text: str, resume_text: str, semantic_score: float) -> Tuple[float, List[str], List[str]]:

    job_skills = extract_skills(job_text)
    resume_skills = extract_skills(resume_text)

    matched = sorted(set(job_skills) & set(resume_skills))
    missing = sorted(set(job_skills) - set(resume_skills))

    skill_ratio = len(matched) / len(job_skills) if job_skills else 0

    # 🔥 improved weighting
    final_score = round(
        (0.6 * semantic_score) + (0.4 * skill_ratio)
        * 100, 2
    )

    return final_score, matched, missing


# ==============================
# 🔥 AI SUMMARY (UPGRADED)
# ==============================

def generate_ai_summary(name, score, matched, missing):

    if score >= 85:
        level = "highly suitable"
    elif score >= 70:
        level = "strong fit"
    elif score >= 50:
        level = "moderate fit"
    else:
        level = "low alignment"

    return f"""
{name} appears to be a {level} candidate.

✔ Strengths: {", ".join(matched[:5]) if matched else "Limited overlap"}

⚠ Gaps: {", ".join(missing[:5]) if missing else "No major gaps"}

This profile shows {level} with the job requirements.
""".strip()
