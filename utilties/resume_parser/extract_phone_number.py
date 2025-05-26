import re

class ExtractPhone:
    def __init__(self):
        pass

    def extract_phone(self, text):
        # Use regex to find phone numbers
        contact_number = None
        pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        match = re.search(pattern, text)
        if match:
            contact_number = match.group()
        return contact_number