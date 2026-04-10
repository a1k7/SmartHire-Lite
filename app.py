import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from advanced_ai import (
    predict_success,
    growth_potential,
    explain_decision,
    simulate_improvement
)
from utils import (
    clean_text,
    extract_text_from_pdf,
    normalize_filename,
    score_resume,
    generate_ai_summary
)

# -------------------------------
# 🔐 USAGE TRACKING SYSTEM
# -------------------------------
USAGE_FILE = "usage.json"
FREE_LIMIT = 17


def load_usage():
    if not os.path.exists(USAGE_FILE):
        return {"count": 0}
    with open(USAGE_FILE, "r") as f:
        return json.load(f)


def save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)


usage = load_usage()

# -------------------------------
# 🔥 LIMIT CHECK
# -------------------------------
remaining = FREE_LIMIT - usage["count"]

st.set_page_config(page_title="SmartHire Lite", page_icon="🚀", layout="wide")

st.title("🚀 SmartHire Lite - AI Resume Screener")

# 🔥 SHOW USAGE STATUS
if remaining <= 0:
    st.error("🚫 Free limit reached (3 resumes). Upgrade to continue.")
    st.info("💡 Contact: Unlock unlimited analysis for your hiring needs.")
    st.stop()
else:
    st.info(f"🟢 Free analyses left: {remaining}")

# -------------------------------
# 🔥 INPUT
# -------------------------------
uploaded_files = st.file_uploader(
    "📌 Upload Resumes (PDF)",
    type=["pdf"],
    accept_multiple_files=True
)

job_desc = st.text_area("🧠 Paste Job Description", height=200)


# -------------------------------
# 🔥 DECISION FUNCTIONS
# -------------------------------
def get_hiring_decision(score):
    if score >= 80:
        return "✅ Strong Hire"
    elif score >= 60:
        return "⚠️ Consider"
    else:
        return "❌ Reject"


def get_urgency(missing_count):
    if missing_count >= 5:
        return "🚨 High Risk – Missing critical skills"
    elif missing_count >= 3:
        return "⚠️ Medium Risk – Some gaps"
    else:
        return "✅ Low Risk"


# -------------------------------
# 🔍 ANALYSIS BUTTON
# -------------------------------
if st.button("🔍 Analyze Candidates"):

    if not uploaded_files or not job_desc.strip():
        st.error("Please upload resumes and enter job description")
        st.stop()

    # 🔥 LIMIT ENFORCEMENT
    if len(uploaded_files) > remaining:
        st.error(f"❌ You can only analyze {remaining} more resumes.")
        st.stop()

    with st.spinner("Analyzing resumes..."):

        job_clean = clean_text(job_desc)

        resumes = []
        names = []

        for file in uploaded_files:
            text = extract_text_from_pdf(file)
            text = clean_text(text)

            resumes.append(text)
            names.append(normalize_filename(file.name))

        # TF-IDF
        docs = resumes + [job_clean]
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf = vectorizer.fit_transform(docs)

        sim_scores = cosine_similarity(tfidf[-1], tfidf[:-1])[0]

        results = []

        for i in range(len(resumes)):
            skill_score, matched, missing = score_resume(
                job_clean, resumes[i], float(sim_scores[i])
            )

            final_score = (skill_score * 0.7) + (sim_scores[i] * 100 * 0.3)
            experience_est = max(1, len(resumes[i]) // 1000)  # simple heuristic

            success_score = predict_success(
               final_score,
               experience_est,
               len(missing)
            )

            growth = growth_potential(len(missing), experience_est)

            explanation = explain_decision(final_score, matched, missing)

            what_if = simulate_improvement(final_score, len(missing))


            results.append({
                "Candidate": names[i],
                "Score (%)": final_score,
                "Matched Skills": matched,
                "Missing Skills": missing,
                "Match Count": len(matched),
                "Missing Count": len(missing),
                "What-if Score(%)":what_if,
                "Growth Potential":growth,
                "Explanation":explanation,
                "Predicted Success(%)":success_score

            })

        df = pd.DataFrame(results)

        # Normalize
        max_score = df["Score (%)"].max()
        if max_score > 0:
            df["Score (%)"] = (df["Score (%)"] / max_score) * 100

        df["Score (%)"] = df["Score (%)"].round(2)

        df = df.sort_values(by="Score (%)", ascending=False).reset_index(drop=True)

        df["Decision"] = df["Score (%)"].apply(get_hiring_decision)
        df["Risk"] = df["Missing Count"].apply(get_urgency)

        df["Matched Skills"] = df["Matched Skills"].apply(lambda x: ", ".join(x[:5]) if x else "—")
        df["Missing Skills"] = df["Missing Skills"].apply(lambda x: ", ".join(x[:5]) if x else "—")

        summaries = []
        for i, row in df.iterrows():
            matched = row["Matched Skills"].split(", ") if row["Matched Skills"] != "—" else []
            missing = row["Missing Skills"].split(", ") if row["Missing Skills"] != "—" else []

            summary = generate_ai_summary(
                row["Candidate"],
                row["Score (%)"],
                matched,
                missing
            )
            summaries.append(summary)

        df["AI Summary"] = summaries

        badges = []
        for i in range(len(df)):
            if i == 0:
                badges.append("🥇 Top Match")
            elif i == 1:
                badges.append("🥈 Strong Match")
            elif i == 2:
                badges.append("🥉 Good Match")
            else:
                badges.append("")
        df.insert(0, "Rank", badges)

        # SAVE CSV
        os.makedirs("output", exist_ok=True)
        df.to_csv("output/results.csv", index=False)

        # 🔥 UPDATE USAGE COUNT
        usage["count"] += len(uploaded_files)
        usage["last_used"] = str(datetime.now())
        save_usage(usage)

    st.success("✅ Analysis Complete")

    # -------------------------------
    # RESULTS UI (UNCHANGED)
    # -------------------------------
    st.subheader("🔥 Final Shortlist (Ready to Contact)")
    for i, row in df.head(3).iterrows():
        st.write(f"{i+1}. **{row['Candidate']}** — {row['Decision']}")

    st.divider()

    st.subheader("🏆 Candidate Breakdown")
    for i, row in df.head(5).iterrows():
        st.markdown(f"### {row['Rank']} {row['Candidate']}")
        st.progress(float(row["Score (%)"]) / 100)

    # 🔥 Advanced AI Features
        st.write(f"📊 **Predicted Success:** {row.get('Predicted_Success', 0)}%")
        st.write(f"🚀 **Growth Potential:** {row.get('Growth_Potential', 'N/A')}")
        st.write(f"🔮 **What-if (after upskilling):** {row.get('WhatIf_Score', 0)}%")

        st.info(f"🧾 **Why this decision?** {row.get('Explanation', 'N/A')}")

    # 🔥 Core Data
        st.write(f"**Score:** {row['Score (%)']}%")
        st.write(f"**Decision:** {row['Decision']}")
        st.write(f"**Risk Level:** {row['Risk']}")

        st.write(f"**Matched Skills:** {row['Matched Skills']}")

    if row["Missing Skills"] != "—":
        st.error(f"🚨 Missing Critical Skills: {row['Missing Skills']}")

    st.write(f"**AI Insight:** {row['AI Summary']}")
    st.divider()

    st.subheader("📊 Full Ranking")
    st.dataframe(df, width="stretch", hide_index=True)

    st.subheader("📈 Score Visualization")
    st.bar_chart(df.set_index("Candidate")["Score (%)"])

    with open("output/results.csv", "rb") as f:
        st.download_button(
            "📥 Download Full Report (CSV)",
            f,
            "SmartHire_Report.csv",
            "text/csv"
        )
