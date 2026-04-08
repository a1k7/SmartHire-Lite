import spacy

nlp = spacy.load("en_core_web_sm")

def extract_skills_from_jd(jd):
    doc = nlp(jd.lower())
    return list(set([token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]))