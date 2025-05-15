import fitz  # PyMuPDF
import spacy
import os
from nameparser import HumanName
import re
import csv
from dateutil import parser
from datetime import datetime

# Load the spaCy model for English
nlp = spacy.load('en_core_web_sm')

class ResumeParser:
    def __init__(self, resume_path=None, debug=False):
        if debug:
            # Use raw string and forward slashes for cross-platform compatibility
            self.resume_path = os.path.join("samples", "resumes", "gayathri_bhat.pdf")
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
    
    def is_likely_section_heading(self, line, keywords):
        """
        Checks if a line is likely a section heading based on formatting and keywords.
        """
        line_clean = line.strip()
        if not line_clean:
            return False

        # Check constraints
        is_short = len(line_clean.split()) <= 5
        no_punct = not any(c in line_clean for c in [":", ".", "-", "•", "(", ")"])
        # has_keyword = any(kw.lower() in line_clean.lower() for kw in keywords)
        has_keyword = any(
            re.match(rf'^(?i){kw}\b$', line_clean) or             # line is exactly keyword
            re.match(rf'^(?i){kw}\b[\s\S]*$', line_clean)         # line starts with keyword
            for kw in keywords
                         )
        is_formatted = (
            line_clean.isupper() or
            line_clean.istitle() or
            line_clean[0].isupper()
        )

        return is_short and no_punct and has_keyword and is_formatted

    
    def extract_experience_section(self, text):
        lines = text.splitlines()
        section_keywords = ['experience', 'employment', 'work history', 'professional background', 'work experience', 'career history',
                            'career summary', 'job history', 'employment history', 'professional experience', 'job experience', 'work summary', 
                            'career experience', 'career details', 'job details', 'job summary', 'employment details', 'work details', 'career overview', 
                            'job overview', 'employment overview']
        stop_keywords = ['education', 'projects', 'skills', 'certifications', 'languages', 'summary', 'objective', 'profile', 'about me', 'interests', 'hobbies', 
                         'awards', 'achievements', 'references', 'extracurricular', 'activities', 'courses', 'training',
                         'seminars', 'conferences', 'workshops', 'publications', 'patents', 'research',
                         'professional affiliations', 'associations']

        start_idx = None
        for i, line in enumerate(lines):
            if self.is_likely_section_heading(line, section_keywords):
                start_idx = i
                break

        if start_idx is None:
            return ""

        # Extract until next section heading
        experience_lines = []
        for line in lines[start_idx + 1:]:
            if self.is_likely_section_heading(line, stop_keywords):
                break
            experience_lines.append(line)

        return "\n".join([lines[start_idx]] + experience_lines)
    
    def extract_date_ranges(self, text):
        """
        Extracts date intervals like 'Jan 2018 – Feb 2021' and returns list of (start_date, end_date).
        Deduplicates based on end_date, keeping the first match based on pattern order.
        """
        patterns = [
            # Jan 2020 – Feb 2023 or January 2020 - Present (with optional dot after month)
            r'([A-Za-z]{3,9}\.?\s+\d{4})\s*(?:–|-|to)\s*([A-Za-z]{3,9}\.?\s+\d{4}|present|current|now)',

            # Jan 20 – Feb 23 or January 20 - Present
            r'([A-Za-z]{3,9}\.?\s+\d{2})\s*(?:–|-|to)\s*([A-Za-z]{3,9}\.?\s+\d{2}|present|current|now)',

            # 01/2020 – 03/2023
            r'(\d{2}/\d{4})\s*(?:–|-|to)\s*(\d{2}/\d{4}|present|current|now)',

            # 2020 – 2023
            r'(\d{4})\s*(?:–|-|to)\s*(\d{4}|present|current|now)',

            # 2020-01 to 2023-03
            r'(\d{4}-\d{2})\s*(?:–|-|to)\s*(\d{4}-\d{2}|present|current|now)',

            # Jan 2024 - current (one-sided pattern)
            r'([A-Za-z]{3,9}\.?)\s+(\d{4})\s*[-–to]+\s*(present|current|now)'
        ]


        seen_end_dates = set()
        date_ranges = []

        for pattern in patterns:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    start, end = match
                elif len(match) == 3:
                    start = f"{match[0]} {match[1]}"
                    end = match[2]
                else:
                    continue

                try:
                    start_date = parser.parse(start, fuzzy=True)
                    end_date = datetime.today() if re.search(r'present|current|now', end, re.IGNORECASE) else parser.parse(end, fuzzy=True)

                    # Use only first matched end_date
                    key = end_date.strftime("%Y-%m-%d")
                    if key not in seen_end_dates:
                        seen_end_dates.add(key)
                        date_ranges.append((start_date, end_date))
                except Exception:
                    continue

        return date_ranges
    
    def extract_total_experience(self, text):
        """
        Takes a list of (start_date, end_date) and returns total years of experience.
        """
        experience_text = self.extract_experience_section(text)
        date_ranges = self.extract_date_ranges(experience_text)
        total_months = 0
        for start, end in date_ranges:
            months = (end.year - start.year) * 12 + (end.month - start.month)
            if months > 0:
                total_months += months

        years = total_months // 12
        months = total_months % 12

        parts = []
        if years:
            parts.append(f"{years} year{'s' if years > 1 else ''}")
        if months:
            parts.append(f"{months} month{'s' if months > 1 else ''}")

        return ' '.join(parts) if parts else "0 months"

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
        total_experience = self.extract_total_experience(resume_text)
        return {'first_name': first_name, 'last_name': last_name, 'email': email, 'phone': phone, 
                'total_experience': total_experience}
