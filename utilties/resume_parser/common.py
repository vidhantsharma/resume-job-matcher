import re

def is_likely_section_heading(line, keywords):
    """
    Checks if a line is likely a section heading based on formatting and keywords.
    """
    line_clean = line.strip()
    if not line_clean:
        return False

    # Check constraints
    is_short = len(line_clean.split()) <= 5
    no_punct = not any(c in line_clean for c in [":", ".", "-", "•", "(", ")"])
    # has_keyword = any(kw.lower() in line_clean.lower() for kw in keywords)
    has_keyword = any(
        re.match(rf'^(?i){kw}\b$', line_clean) or             # line is exactly keyword
        re.match(rf'^(?i){kw}\b[\s\S]*$', line_clean)         # line starts with keyword
        for kw in keywords
                        )
    is_formatted = (
        line_clean.isupper() or
        line_clean.istitle() or
        line_clean[0].isupper()
    )

    return is_short and no_punct and has_keyword and is_formatted