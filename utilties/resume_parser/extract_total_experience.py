import re
from dateutil import parser
from datetime import datetime
from utilties.resume_parser.common import is_likely_section_heading

class ExtractTotalExperience:
    def __init__(self):
        pass

    def extract_total_experience(self, text):
        """
        Takes a list of (start_date, end_date) and returns total years of experience.
        """
        experience_text = self.extract_experience_section(text)
        date_ranges = self.extract_date_ranges(experience_text)
        total_months = 0
        for start, end in date_ranges:
            months = (end.year - start.year) * 12 + (end.month - start.month)
            if months > 0:
                total_months += months

        total_months += 1
        years = total_months // 12
        months = total_months % 12

        parts = []
        if years:
            parts.append(f"{years} year{'s' if years > 1 else ''}")
        if months:
            parts.append(f"{months} month{'s' if months > 1 else ''}")

        return ' '.join(parts) if parts else "0 months"

    def extract_experience_section(self, text):
        lines = text.splitlines()
        section_keywords = ['experience', 'employment', 'work history', 'professional background', 'work experience', 'career history',
                            'career summary', 'job history', 'employment history', 'professional experience', 'job experience', 'work summary', 
                            'career experience', 'career details', 'job details', 'job summary', 'employment details', 'work details', 'career overview', 
                            'job overview', 'employment overview']
        stop_keywords = ['education', 'projects', 'skills', 'certifications', 'languages', 'summary', 'objective', 'profile', 'about me', 'interests', 'hobbies', 
                         'awards', 'achievements', 'references', 'extracurricular', 'activities', 'courses', 'training',
                         'seminars', 'conferences', 'workshops', 'publications', 'patents', 'research',
                         'professional affiliations', 'associations']

        start_idx = None
        for i, line in enumerate(lines):
            if is_likely_section_heading(line, section_keywords):
                start_idx = i
                break

        if start_idx is None:
            return ""

        # Extract until next section heading
        experience_lines = []
        for line in lines[start_idx + 1:]:
            if is_likely_section_heading(line, stop_keywords):
                break
            experience_lines.append(line)

        return "\n".join([lines[start_idx]] + experience_lines)
    
    def extract_date_ranges(self, text):
        """
        Extracts date intervals like 'Jan 2018 – Feb 2021' and returns list of (start_date, end_date).
        Deduplicates based on end_date, keeping the first match based on pattern order.
        """
        patterns = [
            # Jan 2020 – Feb 2023 or January 2020 - Present (with optional dot after month)
            r'([A-Za-z]{3,9}\.?\s+\d{4})\s*(?:–|-|to)\s*([A-Za-z]{3,9}\.?\s+\d{4}|present|current|now)',

            # Jan 20 – Feb 23 or January 20 - Present
            r'([A-Za-z]{3,9}\.?\s+\d{2})\s*(?:–|-|to)\s*([A-Za-z]{3,9}\.?\s+\d{2}|present|current|now)',

            # 01/2020 – 03/2023
            r'(\d{2}/\d{4})\s*(?:–|-|to)\s*(\d{2}/\d{4}|present|current|now)',

            # 2020 – 2023
            r'(\d{4})\s*(?:–|-|to)\s*(\d{4}|present|current|now)',

            # 2020-01 to 2023-03
            r'(\d{4}-\d{2})\s*(?:–|-|to)\s*(\d{4}-\d{2}|present|current|now)',

            # Jan 2024 - current (one-sided pattern)
            r'([A-Za-z]{3,9}\.?)\s+(\d{4})\s*[-–to]+\s*(present|current|now)'
        ]


        seen_end_dates = set()
        date_ranges = []

        for pattern in patterns:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    start, end = match
                elif len(match) == 3:
                    start = f"{match[0]} {match[1]}"
                    end = match[2]
                else:
                    continue

                try:
                    start_date = parser.parse(start, fuzzy=True)
                    end_date = datetime.today() if re.search(r'present|current|now', end, re.IGNORECASE) else parser.parse(end, fuzzy=True)

                    # Use only first matched end_date
                    key = end_date.strftime("%Y-%m-%d")
                    if key not in seen_end_dates:
                        seen_end_dates.add(key)
                        date_ranges.append((start_date, end_date))
                except Exception:
                    continue

        return date_ranges