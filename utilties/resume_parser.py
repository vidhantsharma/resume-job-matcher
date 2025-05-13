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
            self.resume_path = os.path.join("samples", "resumes", "vidhant_resume.pdf")
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
    
    def extract_email(self, text):
        # Use regex to find email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""
    
    def extract_phone(self, text):
        # Use regex to find phone numbers
        contact_number = None
        pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        match = re.search(pattern, text)
        if match:
            contact_number = match.group()
        return contact_number

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
        email = self.extract_email(resume_text)
        phone = self.extract_phone(resume_text)
        return {'first_name': first_name, 'last_name': last_name, 'email': email, 'phone': phone}
