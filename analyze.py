from fastapi import APIRouter, UploadFile, File, Form
from backend.services.parser import parse_resume
from backend.services.jd_extractor import extract_skills
from backend.services.scorer import calculate_score
from backend.services.summary import generate_summary

router = APIRouter()

@router.post("/analyze")
async def analyze(job_desc: str = Form(...), file: UploadFile = File(...)):
    
    resume_text = await file.read()
    resume_data = parse_resume(resume_text)

    jd_skills = extract_skills(job_desc)

    result = calculate_score(resume_data, jd_skills)
    summary = generate_summary(result)

    return {
        "result": result,
        "summary": summary
    }