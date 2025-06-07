import os
import ast
import csv
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from llama_cpp import Llama
import re


class ExtractSkills:
    def __init__(self, csv_file="data/skills.csv", gemma_model_path=r"llm_model\gemma\gemma-2-9b-it-Q4_K_M.gguf"):
        self.csv_file = csv_file
        self.gemma_model_path = gemma_model_path

    def extract_skills(self, text):
        """
        Extract skills from resume text using multiple methods:
        1. CSV keyword matching
        2. NER model
        3. LLM (Gemma 2)
        
        Returns a set of unique skills.
        """
        csv_skills = self.extract_skills_from_csv(text)
        ner_skills = self.extract_skills_from_ner(text)
        llm_skills = self.extract_skills_from_llm(text)

        return list(csv_skills.union(ner_skills).union(llm_skills))
    
    def extract_skills_from_csv(self, text, csv_file="data/skills.csv"):
        skills = set()
        try:
            with open(csv_file, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    keyword = row[0].strip().lower()
                    if keyword in text.lower():
                        skills.add(keyword.title())
        except Exception as e:
            print(f"[ERROR] CSV skill extraction: {e}")
        return skills

    def clean_skill(self, word):
        # Keep only allowed chars (letters, digits, space, + . -)
        word = ''.join(c for c in word if c.isalnum() or c.isspace() or c in ['+', '.', '-'])
        # Strip leading/trailing spaces and punctuation like - + . 
        word = word.strip(" -+.")
        # Replace multiple spaces or spaces around punctuation with single space
        word = re.sub(r'\s*([+\-\.])\s*', r'\1', word)  # remove spaces around + - .
        word = re.sub(r'\s+', ' ', word)  # multiple spaces → one space
        return word

    def extract_skills_from_ner(self, text, use_custom_model=False):
        try:
            if use_custom_model:
                model_dir = "ner_model/skill_ner_model"
                tokenizer = AutoTokenizer.from_pretrained(model_dir)
                model = AutoModelForTokenClassification.from_pretrained(model_dir)
            else:
                model_name = "Nucha/Nucha_SkillNER_BERT"
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForTokenClassification.from_pretrained(model_name)

            ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="max")

            pattern = re.compile(r'^[\w\s\+\.\-]+$')

            entities = ner_pipeline(text)
            skills = set()
            for ent in entities:
                if ent['entity_group'].upper() == "HSKILL":
                    word = ent['word'].strip()
                    word = self.clean_skill(word)
                    if len(word) >= 3 and pattern.match(word):
                        skills.add(word.title())
            return skills
        except Exception as e:
            print(f"[ERROR] NER skill extraction: {e}")
            return set()


    def extract_skills_from_llm(self, text, gemma_model_path=r"llm_model\gemma\gemma-2-9b-it-Q4_K_M.gguf"):
        try:
            llm = Llama(
                model_path=gemma_model_path,
                n_ctx=2048,
                n_threads=8,
                n_batch=32,
                verbose=False
            )

            prompt = f"""You are an expert HR assistant.
Given the following resume text, extract only relevant skills.
Respond with a Python list of skills as strings.

Resume:
{text}

Skills:
"""
            # Generate completion
            response = llm(prompt, max_tokens=256, stop=["</s>", "\n\n"])

            # 'response' is a dict with 'choices', each having 'text'
            output = response['choices'][0]['text']

            # Convert string list output to Python list
            skills = ast.literal_eval(output.strip())

            # Return skills as a set, title-cased
            return set(s.strip().title() for s in skills if isinstance(s, str))
        except Exception as e:
            print(f"[ERROR] LLM skill extraction: {e}")
            return set()
