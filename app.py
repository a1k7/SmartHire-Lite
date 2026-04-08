import os
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import (
    clean_text,
    extract_text_from_pdf,
    normalize_filename,
    score_resume,
    generate_ai_summary
)

# 🔥 NEW: Hiring Decision Logic
def get_hiring_decision(score):
    if score >= 80:
        return "✅ Strong Hire"
    elif score >= 60:
        return "⚠️ Consider"
    else:
        return "❌ Reject"

# 🔥 NEW: Urgency Signal
def get_urgency(missing_count):
    if missing_count >= 5:
        return "🚨 High Risk – Missing critical skills"
    elif missing_count >= 3:
        return "⚠️ Medium Risk – Some gaps"
    else:
        return "✅ Low Risk"

st.set_page_config(page_title="SmartHire Lite", page_icon="🚀", layout="wide")

st.title("🚀 SmartHire Lite - AI Resume Screener")

uploaded_files = st.file_uploader(
    "📌 Upload Resumes (PDF)", type=["pdf"], accept_multiple_files=True
)

job_desc = st.text_area("🧠 Paste Job Description", height=200)

if st.button("🔍 Analyze Candidates"):

    if not uploaded_files or not job_desc.strip():
        st.error("Please upload resumes and enter job description")
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

        # 🔥 TF-IDF Similarity
        docs = resumes + [job_clean]
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf = vectorizer.fit_transform(docs)

        sim_scores = cosine_similarity(tfidf[-1], tfidf[:-1])[0]

        results = []

        # 🔥 BUILD RESULTS
        for i in range(len(resumes)):
            skill_score, matched, missing = score_resume(
                job_clean, resumes[i], float(sim_scores[i])
            )

            # 🔥 HYBRID SCORE (REALISTIC)
            final_score = (skill_score * 0.7) + (sim_scores[i] * 100 * 0.3)

            results.append({
                "Candidate": names[i],
                "Score (%)": final_score,
                "Matched Skills": matched,
                "Missing Skills": missing,
                "Match Count": len(matched),
                "Missing Count": len(missing)
            })

        df = pd.DataFrame(results)

        # 🔥 NORMALIZE SCORE
        max_score = df["Score (%)"].max()
        if max_score > 0:
            df["Score (%)"] = (df["Score (%)"] / max_score) * 100

        df["Score (%)"] = df["Score (%)"].round(2)

        # 🔥 SORT
        df = df.sort_values(by="Score (%)", ascending=False).reset_index(drop=True)

        # 🔥 DECISION + URGENCY
        df["Decision"] = df["Score (%)"].apply(get_hiring_decision)
        df["Risk"] = df["Missing Count"].apply(get_urgency)

        # 🔥 CONVERT LIST → STRING (for UI)
        df["Matched Skills"] = df["Matched Skills"].apply(lambda x: ", ".join(x[:5]) if x else "—")
        df["Missing Skills"] = df["Missing Skills"].apply(lambda x: ", ".join(x[:5]) if x else "—")

        # 🔥 AI SUMMARY
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

        # 🔥 RANK BADGES
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

    st.success("✅ Analysis Complete")

    # 🔥 FINAL SHORTLIST (SELLING FEATURE)
    st.subheader("🔥 Final Shortlist (Ready to Contact)")

    for i, row in df.head(3).iterrows():
        st.write(f"{i+1}. **{row['Candidate']}** — {row['Decision']}")

    st.divider()

    # 🔥 TOP CANDIDATES (HIGH IMPACT UI)
    st.subheader("🏆 Candidate Breakdown")

    for i, row in df.head(5).iterrows():
        st.markdown(f"### {row['Rank']} {row['Candidate']}")
        st.progress(row["Score (%)"] / 100)

        st.write(f"**Score:** {row['Score (%)']}%")
        st.write(f"**Decision:** {row['Decision']}")
        st.write(f"**Risk Level:** {row['Risk']}")

        st.write(f"**Matched Skills:** {row['Matched Skills']}")

        if row["Missing Skills"] != "—":
            st.error(f"🚨 Missing Critical Skills: {row['Missing Skills']}")

        st.write(f"**AI Insight:** {row['AI Summary']}")

        st.divider()

    # 🔥 FULL TABLE
    st.subheader("📊 Full Ranking")
    st.dataframe(df, width="stretch", hide_index=True)

    # 🔥 AI INSIGHTS
    st.subheader("🤖 AI Candidate Insights")

    for i, row in df.head(3).iterrows():
        with st.expander(f"{row['Candidate']} ({row['Score (%)']}%)"):
            st.write(row["AI Summary"])

    # 🔥 CHART
    st.subheader("📈 Score Visualization")
    st.bar_chart(df.set_index("Candidate")["Score (%)"])

    # 🔥 DOWNLOAD
    with open("output/results.csv", "rb") as f:
        st.download_button(
            "📥 Download Full Report (CSV)",
            f,
            "SmartHire_Report.csv",
            "text/csv"
        )