import fitz  # PyMuPDF
import spacy
import os
from nameparser import HumanName
import re
import csv

# Load the spaCy model for English
nlp = spacy.load('en_core_web_sm')

class ResumeParser:
    def __init__(self, resume_path=None, debug=False):
        if debug:
            # Use raw string and forward slashes for cross-platform compatibility
            self.resume_path = os.path.join("samples", "resumes", "MANISH_KUMAR_SINGH.pdf")
        else:
            if not resume_path:
                raise ValueError("resume_path must be provided when debug is False")
            self.resume_path = resume_path

    def parse(self):
        # read the resume file
        with open(self.resume_path, "rb") as file:
            resume_binary = file.read()
        resume_text = self.extract_resume_info_from_pdf(resume_binary)
        resume_info = self.extract_resume_info(resume_text)
        return resume_info
    
    def extract_name(self, text):
        lines = text.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip() != ""]

        # Consider only top 10 lines
        for line in lines[:10]:
            # Skip lines with contact details or headings
            if re.search(r'[\d@]|curriculum|resume|cv', line.lower()):
                continue

            # Try parsing name with HumanName
            name = HumanName(line)
            if name.first and name.last:
                return name.first, name.last

        # Fallback: try spaCy NER only on first 10 lines
        first_10_lines = "\n".join(lines[:10])
        doc = nlp(first_10_lines)
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                name = HumanName(ent.text)
                if name.first and name.last:
                    return name.first, name.last

        return "", ""

    # Load skills from CSV file
    def load_skills_from_csv(self, csv_file):
        skills = set()
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                skills.add(row[0].strip().lower())  # Add skill to the set (convert to lowercase for case-insensitive comparison)
        return skills

    def extract_resume_info_from_pdf(self, binary_pdf):
        doc = fitz.open(stream=binary_pdf, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def extract_resume_info(self, resume_text):
        # Extract relevant information from the resume text
        first_name, last_name = self.extract_name(resume_text)
        return {'first_name': first_name, 'last_name': last_name}
