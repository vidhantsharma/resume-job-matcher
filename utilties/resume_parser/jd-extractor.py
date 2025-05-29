from typing import Optional, List
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import PyMuPDFLoader

class JobDescription(BaseModel):
    job_title: str = Field(default="Not specified", description="The main job title/position")
    company_name: Optional[str] = Field(default=None, description="Company name")
    location: Optional[str] = Field(default=None, description="Job location")
    job_type: Optional[str] = Field(default=None, description="Employment type")
    experience_required: Optional[str] = Field(default=None, description="Required experience")
    education_level: Optional[str] = Field(default=None, description="Required education")
    technical_skills: List[str] = Field(default_factory=list, description="Technical skills")
    soft_skills: List[str] = Field(default_factory=list, description="Soft skills")
    responsibilities: List[str] = Field(default_factory=list, description="Job responsibilities")
    salary_range: Optional[str] = Field(default=None, description="Salary information")
    benefits: List[str] = Field(default_factory=list, description="Benefits information")  # Changed to List[str]
    company_size: Optional[str] = Field(default=None, description="Company size")
    industry: Optional[str] = Field(default=None, description="Industry")

class JobDescriptionExtractor:
    def __init__(self, model_name: str = "gemma2:9b-instruct-q4_K_M"):
        print(f"🚀 Initializing Job Description Extractor with model: {model_name}")
        
        self.llm = OllamaLLM(
            model=model_name,
            temperature=0.1,
            num_gpu=40,  # Force GPU usage
        )
        
        self.output_parser = PydanticOutputParser(pydantic_object=JobDescription)
        
        self.prompt = ChatPromptTemplate.from_template(
            """You are an expert job description analyzer. Extract information and respond ONLY with valid JSON. \
CRITICAL REQUIREMENTS:
- You MUST respond with a valid JSON object following the exact schema below
- Extract ONLY information explicitly mentioned in the job description
- If information is missing, use null for strings or [] for arrays
- DO NOT add explanations, comments, or text outside the JSON
- DO NOT use markdown formatting or code blocks
JSON SCHEMA REQUIRED:
{{
    "job_title": "string (job title/position name)",
    "company_name": "string or null (company name)",
    "location": "string or null (job location)",
    "job_type": "string or null (full-time/part-time/contract)",
    "experience_required": "string or null (years of experience)",
    "education_level": "string or null (degree requirements)",
    "technical_skills": ["array of technical skills"],
    "soft_skills": ["array of soft skills"],
    "responsibilities": ["array of job duties"],
    "salary_range": "string or null (salary info)",
    "benefits": "string or null (benefits info)",
    "company_size": "string or null (company size)",
    "industry": "string or null (industry/domain)"
}}

JOB DESCRIPTION TEXT:
{job_text}

JSON OUTPUT:"""
        )
        
        self.extraction_chain = (
            self.prompt
            | self.llm
            | self.output_parser
        )
        
        print("✅ Extractor initialized successfully!")
    
    def extract_from_pdf(self, pdf_path: str):
        try:
            print("📄 Loading PDF...")
            loader = PyMuPDFLoader(file_path=pdf_path)
            documents = loader.load()
            
            job_text = "\n".join([doc.page_content for doc in documents])
            print(f"📝 Extracted {len(job_text)} characters from PDF")
            
            print("🤖 Processing with LLM... (this may take 30-60 seconds)")
            
            # FIX: Direct invocation with better error handling
            raw_response = self.llm.invoke(self.prompt.format(job_text=job_text))
            
            print(f"🔍 Raw LLM response: {raw_response[:300]}...")  # Show more of response
            
            # FIX: Try to clean the response if it has extra text
            import json
            import re
            
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                print(f"🔧 Extracted JSON: {json_str[:200]}...")
                
                # Parse manually first to check
                try:
                    parsed_data = json.loads(json_str)
                    print(f"✅ JSON parsed successfully: {len(parsed_data)} fields")
                    
                    # Create JobDescription object manually
                    result = JobDescription(**parsed_data)
                    return result
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed: {e}")
                    print(f"Raw JSON: {json_str}")
                    
            # Fallback: try original parser
            result = self.output_parser.parse(raw_response)
            return result
            
        except Exception as e:
            print(f"❌ Error during extraction: {e}")
            print(f"Full response: {raw_response if 'raw_response' in locals() else 'No response'}")
            
            # Return default object with some basic extraction
            return JobDescription(
                job_title="Manual Review Required",
                company_name="Check PDF manually",
                technical_skills=["Review needed"],
                responsibilities=["Check original document"]
            )

def main():
    print("Job Description Extractor")
    print("=" * 40)
    
    pdf_path = input("\n📁 Enter the PDF file path: ").strip()
    
    print(f"\n📄 Processing: {pdf_path}")
    print("⏳ Extracting data... (this may take a moment)")
    
    try:
        extractor = JobDescriptionExtractor()
        result = extractor.extract_from_pdf(pdf_path)
        
        # Display results
        print("🎉 EXTRACTION RESULTS:")
        print("========================================")
        print(f"📋 Job Title: {result.job_title if result.job_title else 'Not specified'}")
        print(f"🏢 Company Name: {result.company_name if result.company_name else 'Not specified'}")
        print(f"📍 Location: {result.location if result.location else 'Not specified'}")
        print(f"🕒 Job Type: {result.job_type if result.job_type else 'Not specified'}")
        print(f"⏱️ Experience Required: {result.experience_required if result.experience_required else 'Not specified'}")
        print(f"🎓 Education Level: {result.education_level if result.education_level else 'Not specified'}")
        print(f"💰 Salary Range: {result.salary_range if result.salary_range else 'Not specified'}")
        print(f"🎁 Benefits: {result.benefits if result.benefits else 'Not specified'}")
        print(f"🏭 Company Size: {result.company_size if result.company_size else 'Not specified'}")
        print(f"🌐 Industry: {result.industry if result.industry else 'Not specified'}")

        print(f"\n💻 Technical Skills ({len(result.technical_skills)}):")
        if result.technical_skills:
            for skill in result.technical_skills:
                print(f"   • {skill}")
        else:
            print("   • None specified")

        print(f"\n🤝 Soft Skills ({len(result.soft_skills)}):")
        if result.soft_skills:
            for skill in result.soft_skills:
                print(f"   • {skill}")
        else:
            print("   • None specified")

        print(f"\n📝 Responsibilities ({len(result.responsibilities)}):")
        if result.responsibilities:
            for resp in result.responsibilities:
                print(f"   • {resp}")
        else:
            print("   • None specified")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
