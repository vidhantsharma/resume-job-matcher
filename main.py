from utilties.job_description_parser.job_description_parser import JobDescriptionParser
from utilties.resume_parser.resume_parser import ResumeParser
import os

def get_parsed_resume_data(resume_text):
    resume_parser = ResumeParser(resume_binary=resume_text)
    resume_data = resume_parser.parse()
    return resume_data

def get_parsed_jd_data(jd_text):
    # Dummy implementation; replace with actual logic
    return {
        "Skills": ["Python", "MLOps", "Machine Learning", "NLP"]
    }

# def main():
#     # Example usage
#     resume_path = os.path.join("samples", "resumes", "vidhant_resume.pdf")
#     job_description_path = "path/to/job_description.txt"

#     # Parse the resume
#     resume_parser = ResumeParser(resume_path)
#     resume_data = resume_parser.parse()
#     print("Resume Data:", resume_data)

#     # Parse the job description
#     job_description_parser = JobDescriptionParser(job_description_path)
#     job_description_data = job_description_parser.parse()


# if __name__ == "__main__":
#     print("Starting Resume and Job Description Parser...")
#     main()