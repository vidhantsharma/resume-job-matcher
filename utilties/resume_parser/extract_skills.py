import csv

class ExtractSkills:
    def __init__(self):
        pass

    def extract_skills(self):
        # Placeholder for the actual skill extraction logic
        return []
    
    # Load skills from CSV file
    def load_skills_from_csv(self, csv_file):
        skills = set()
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                skills.add(row[0].strip().lower())  # Add skill to the set (convert to lowercase for case-insensitive comparison)
        return skills