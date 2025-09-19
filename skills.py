import spacy

# Load spaCy English model (already installed via requirements.txt)
nlp = spacy.load("en_core_web_sm")

# Predefined skills list
skills_list = [
    'python', 'java', 'sql', 'machine learning', 'data analysis',
    'excel', 'aws', 'docker', 'fastapi', 'pandas'
]

# Extract skills from text
def extract_skills(text):
    text = text.lower()
    extracted_skills = [skill for skill in skills_list if skill in text]
    return extracted_skills

# Calculate match score between CV skills and JD skills
def calculate_score(cv_skills, jd_skills):
    if not jd_skills:
        return 0
    matched = len(set(cv_skills) & set(jd_skills))
    score = (matched / len(jd_skills)) * 100
    return round(score, 2)
