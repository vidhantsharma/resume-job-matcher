from utilties.job_description_parser import JobDescriptionParser
from utilties.resume_parser import ResumeParser

DEBUG = True

def main():
    # Example usage
    resume_path = "path/to/resume.pdf"
    job_description_path = "path/to/job_description.txt"

    # Parse the resume
    resume_parser = ResumeParser(resume_path, debug=DEBUG)
    resume_data = resume_parser.parse()
    print("Resume Data:", resume_data)

    # Parse the job description
    job_description_parser = JobDescriptionParser(job_description_path, debug=DEBUG)
    # job_description_data = job_description_parser.parse()


if __name__ == "__main__":
    print("Starting Resume and Job Description Parser...")
    main()