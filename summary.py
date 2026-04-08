def generate_summary(result):
    summary = f"""
📊 Candidate Evaluation Report

✅ Match Score: {result['match_score']}%
📈 Final Score: {result['final_score']}%

🟢 Strengths:
- Skills matched: {", ".join(result['matched_skills'][:5])}

🔴 Weaknesses:
- Missing critical skills: {", ".join(result['missing_skills'][:5])}

💡 Recommendation:
"""
    if result["decision"] == "Accept":
        summary += "Candidate is a strong fit. Proceed with interview."
    else:
        summary += "Candidate needs improvement before shortlist."

    return summary