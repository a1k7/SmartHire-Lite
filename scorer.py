import re

def calculate_score(resume_data, jd_skills):
    resume_skills = set([s.lower() for s in resume_data["skills"]])
    jd_skills = set([s.lower() for s in jd_skills])

    matched = resume_skills.intersection(jd_skills)
    missing = jd_skills - resume_skills
    extra = resume_skills - jd_skills

    match_score = len(matched) / (len(jd_skills) + 1e-5) * 100

    # Section-wise scoring (simple heuristic)
    experience_score = min(len(resume_data.get("experience", [])) * 10, 100)
    education_score = 70 if resume_data.get("education") else 40

    final_score = (0.6 * match_score + 0.25 * experience_score + 0.15 * education_score)

    decision = "Accept" if final_score > 65 else "Reject"
    risk = "Low" if final_score > 70 else "Medium" if final_score > 40 else "High"

    return {
        "final_score": round(final_score, 2),
        "match_score": round(match_score, 2),
        "experience_score": experience_score,
        "education_score": education_score,
        "matched_skills": list(matched),
        "missing_skills": list(missing),
        "extra_skills": list(extra),
        "decision": decision,
        "risk": risk
    }