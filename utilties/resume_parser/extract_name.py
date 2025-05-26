import re
from nameparser import HumanName
import spacy

# Load the spaCy model for English
nlp = spacy.load('en_core_web_sm')

class ExtractName:
    def __init__(self):
        pass

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