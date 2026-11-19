import re


SKILLS = [
    "python", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "sql", "mysql", "postgresql", "mongodb", "excel", "power bi", "tableau",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux",
    "java", "javascript", "typescript", "react", "node.js", "django",
    "flask", "fastapi", "html", "css", "machine learning", "deep learning",
    "nlp", "natural language processing", "data analysis", "data visualization",
]


def extract_skills(text: str) -> list[str]:
    cleaned = " " + text.lower() + " "
    found = []
    for skill in SKILLS:
        escaped = re.escape(skill)
        pattern = rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"
        if re.search(pattern, cleaned):
            found.append(skill)
    return sorted(found)


def extract_years_experience(text: str) -> float:
    matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*(?:\+?\s*)?(?:years?|yrs?|y)\b",
        text.lower(),
    )
    return max((float(value) for value in matches), default=0.0)

