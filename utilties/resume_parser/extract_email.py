import re

class ExtractEmail:
    def __init__(self):
        pass

    def extract_email(self, text):
        # Use regex to find email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""