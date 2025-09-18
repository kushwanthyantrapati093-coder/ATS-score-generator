import pdfplumber
from docx import Document

# Extract text from PDF
def extract_pdf(file):
    text = ''
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text

# Extract text from DOCX
def extract_docx(file):
    doc = Document(file)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

# Extract text from TXT
def extract_txt(file):
    return file.read().decode("utf-8")
