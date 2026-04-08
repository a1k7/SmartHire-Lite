import spacy
import PyPDF2

nlp = spacy.load("en_core_web_sm")

def extract_text(file):
    pdf = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""
    return text

def extract_skills(text):
    doc = nlp(text.lower())
    skills = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]
    return list(set(skills))

def parse_resume(file):
    text = extract_text(file)
    skills = extract_skills(text)
    return {"text": text, "skills": skills}