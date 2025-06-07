import spacy
import fitz

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_skills_from_text(text, model_path="skill_ner_model"):
    # nlp = spacy.load(model_path)
    # doc = nlp(text)
    # print("Entities found:", [(ent.text, ent.label_) for ent in doc.ents])
    # skills = set()
    # for ent in doc.ents:
    #     if ent.label_ == "SKILL":
    #         skill_text = ''.join(filter(str.isalpha, ent.text))
    #         if skill_text:
    #             skills.add(skill_text)
    # return skills

    non_skill_labels = {'DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL', 'EMAIL'}
    
    skills = set()
    nlp_skills = spacy.load(model_path)
    for ent in nlp_skills(text).ents:
        if ent.label_ == 'SKILL':
            # Check if the entity text is not in the non-skill labels set
            if ent.label_ not in non_skill_labels and not ent.text.isdigit():
                # Filter out non-alphabetic characters
                skill_text = ''.join(filter(str.isalpha, ent.text))
                if skill_text:
                    skills.add(skill_text)
    return skills

if __name__ == "__main__":
    pdf_path = r"samples\resumes\vidhant_resume.pdf"
    model_path = r"model\skills"
    resume_text = extract_text_from_pdf(pdf_path)
    resume_text = ' '.join(resume_text.split())  # Clean whitespace
    skills = extract_skills_from_text(resume_text, model_path=model_path)
    print("Extracted Skills:")
    for skill in skills:
        print("-", skill)
