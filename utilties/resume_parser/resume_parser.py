import fitz  # PyMuPDF
from utilties.resume_parser.extract_name import ExtractName
from utilties.resume_parser.extract_email import ExtractEmail
from utilties.resume_parser.extract_phone_number import ExtractPhone
from utilties.resume_parser.extract_total_experience import ExtractTotalExperience
from utilties.resume_parser.extract_education import ExtractEducation
from utilties.resume_parser.extract_skills import ExtractSkills

class ResumeParser:
    def __init__(self, resume_path=None):
        self.resume_path = resume_path

    def parse(self):
        # read the resume file
        with open(self.resume_path, "rb") as file:
            resume_binary = file.read()
        resume_text = self.extract_resume_info_from_pdf(resume_binary)
        resume_info = self.extract_resume_info(resume_text)
        return resume_info
    
    def extract_resume_info_from_pdf(self, binary_pdf):
        doc = fitz.open(stream=binary_pdf, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def extract_resume_info(self, resume_text):
        # Extract relevant information from the resume text
        name_extractor = ExtractName()
        first_name, last_name = name_extractor.extract_name(resume_text)

        email_extractor = ExtractEmail()
        email = email_extractor.extract_email(resume_text)

        phone_extractor = ExtractPhone()
        phone = phone_extractor.extract_phone(resume_text)

        total_experience_extractor = ExtractTotalExperience()
        total_experience = total_experience_extractor.extract_total_experience(resume_text)

        education_extractor = ExtractEducation()
        education = education_extractor.extract_education(resume_text)
        
        return {'first_name': first_name, 'last_name': last_name, 'email': email, 'phone': phone, 
                'total_experience': total_experience, 'education': education}
