import spacy
import re
import csv
from utilties.resume_parser.common import is_likely_section_heading

# Load the spaCy model for English
nlp = spacy.load('en_core_web_sm')

class ExtractEducation:
    def __init__(self):
        pass
    
    def extract_education(self, text):
        lines = text.splitlines()
        education_keywords = ['education', 'academics', 'qualification', 'educational background', 'academic background']
        stop_keywords = ['experience', 'skills', 'projects', 'certifications', 'summary', 'contact', 'profile', 'about me', 'interests', 'hobbies',
                         'awards', 'achievements', 'references', 'extracurricular', 'activities', 'courses', 'training',
                         'seminars', 'conferences', 'workshops', 'publications', 'patents', 'research',
                         'professional affiliations', 'associations', 'languages', 'work experience', 'career summary', 'job history',
                         'employment history', 'professional experience', 'job experience', 'work summary', 'technical expertise and skills',
                         'academic projects' ]
        
        # Locate the education section
        start_idx = None
        for i, line in enumerate(lines):
            if is_likely_section_heading(line, education_keywords):
                start_idx = i
                break
        
        if start_idx is None:
            return []

        education_lines = []
        for line in lines[start_idx + 1:]:
            if is_likely_section_heading(line, stop_keywords):
                break
            education_lines.append(line.strip())

        education_text = "\n".join(education_lines)

        # Use spaCy to extract university/college names
        universities = self.extract_universities(education_text)
        # doc = nlp(education_text)
        # universities = [ent.text for ent in doc.ents if ent.label_ == "ORG" and any(kw in ent.text.lower() for kw in ["university", "college", "institute", "iit", "iiit", "nit", "iisc"])]

        # Extract degrees using regex
        degree_pattern = r"\b(?:B\.?\s?Tech|M\.?\s?Tech|B\.?\s?E|M\.?\s?E|B\.?\s?Sc|M\.?\s?Sc|B\.?\s?C\.?\s?A|M\.?\s?C\.?\s?A|B\.?\s?A|M\.?\s?A|MBA|Ph\.?\s?D|Bachelor(?:\s+of\s+(?:Technology|Science|Engineering|Arts|Computer\s+Applications))?|Master(?:\s+of\s+(?:Technology|Science|Engineering|Arts|Business\s+Administration|Computer\s+Applications)))(?:/\s?(?:B\.?\s?Tech|M\.?\s?Tech|B\.?\s?E|M\.?\s?E|B\.?\s?Sc|M\.?\s?Sc|B\.?\s?C\.?\s?A|M\.?\s?C\.?\s?A|B\.?\s?A|M\.?\s?A|MBA|Ph\.?\s?D))?\b"

        degrees = re.findall(degree_pattern, education_text, re.IGNORECASE)

        majors = self.extract_major(education_text)

        return {
            "degrees": list(set(degrees)),
            "institutions": universities,
            "majors": majors
        }
    
    def extract_universities(self, text):
        universities = []

        # Regex pattern to match institutes with optional hyphen or space and ignore case
        pattern = r"\b(?:" \
                r"IISc[-\s]?(?:Bangalore|Bengaluru|Bangaluru)|" \
                r"IIT[-\s]?[A-Z][a-z]+|" \
                r"NIT[-\s]?[A-Z][a-z]+|" \
                r"IIIT[-\s]?[A-Z][a-z]+|" \
                r"BITS[-\s]?[A-Z][a-z]+)\b"

        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        universities.extend(matches)

        # spaCy-based fallback
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            doc = nlp(line)
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    org_text = ent.text.strip()
                    if any(keyword in org_text.lower() for keyword in ["university", "college", "institute", "iit", "iiit", "nit", "iisc", "bits", "bit", "vit", ]):
                        universities.append(org_text)

        return list(set(universities))  # Remove duplicates
    
    def extract_major(self, text):
        doc = nlp(text)
        major_keywords = self.load_major_keywords('data/majors.csv')
        major_keywords.remove("Major")
        majors = []
        for keyword in major_keywords:
            if keyword.lower() in doc.text.lower():
                majors.append(keyword)

        return list(set(majors))  # Return unique majors
    
    def load_major_keywords(self, file_path):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            return set(row[0] for row in reader)