from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .skills import extract_skills, extract_years_experience
from .text_processing import clean_text, read_resume


def score_resumes(
    resume_directory: str,
    job_description: str,
    must_have_skills: list[str],
    minimum_years: float = 0.0,
    shortlist_threshold: float = 50.0,
    nice_to_have_skills: list[str] | None = None,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    score_weights = weights or {
        "similarity": 0.55,
        "skills": 0.35,
        "experience": 0.10,
    }
    total_weight = sum(score_weights.values())
    if total_weight <= 0:
        raise ValueError("Scoring weights must have a positive total")

    normalized_weights = {
        key: float(value) / total_weight
        for key, value in score_weights.items()
    }
    nice_to_have = {
        skill.strip().lower()
        for skill in (nice_to_have_skills or [])
        if skill.strip()
    }
    resume_paths = sorted(
        path
        for path in Path(resume_directory).iterdir()
        if path.is_file() and path.suffix.lower() in {".txt", ".pdf", ".docx"}
    )
    if not resume_paths:
        raise ValueError(f"No TXT, PDF, or DOCX resumes found in {resume_directory}")

    rows = []
    resume_texts = []
    raw_text_by_name = {}

    for path in resume_paths:
        try:
            raw_text = read_resume(str(path))
        except (RuntimeError, ValueError) as exc:
            rows.append({
                "candidate": path.stem,
                "resume_file": path.name,
                "match_score": 0.0,
                "matched_skills": "",
                "missing_must_have": "",
                "experience_years": 0.0,
                "experience_gap": minimum_years,
                "decision": "Review",
                "error": str(exc),
                "similarity_score": 0.0,
                "skill_coverage": 0.0,
                "experience_score": 0.0,
                "nice_to_have_matches": "",
            })
            continue

        cleaned = clean_text(raw_text)
        resume_texts.append(cleaned)
        raw_text_by_name[path.name] = raw_text

    valid_paths = [
        path for path in resume_paths
        if path.name in raw_text_by_name
    ]

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    vectors = vectorizer.fit_transform([clean_text(job_description), *resume_texts])
    similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    valid_index = 0
    for path in resume_paths:
        if path.name not in raw_text_by_name:
            continue

        raw_text = raw_text_by_name[path.name]
        cleaned = clean_text(raw_text)
        resume_skills = set(extract_skills(cleaned))
        must_have = {skill.strip().lower() for skill in must_have_skills if skill.strip()}
        matched = sorted(skill for skill in must_have if skill in resume_skills)
        missing = sorted(skill for skill in must_have if skill not in resume_skills)
        years = extract_years_experience(raw_text)

        similarity_score = float(similarities[valid_index]) * 100
        skill_coverage = (len(matched) / len(must_have) * 100) if must_have else 100.0
        experience_score = min(years / minimum_years, 1.0) * 100 if minimum_years > 0 else 100.0
        nice_matches = sorted(skill for skill in nice_to_have if skill in resume_skills)
        nice_bonus = (len(nice_matches) / len(nice_to_have) * 5.0) if nice_to_have else 0.0
        final_score = (
            normalized_weights.get("similarity", 0.0) * similarity_score
            + normalized_weights.get("skills", 0.0) * skill_coverage
            + normalized_weights.get("experience", 0.0) * experience_score
            + nice_bonus
        )
        final_score = min(final_score, 100.0)

        decision = "Shortlist" if final_score >= shortlist_threshold and not missing else "Reject"
        if final_score >= shortlist_threshold and missing:
            decision = "Review"

        rows.append({
            "candidate": path.stem,
            "resume_file": path.name,
            "match_score": round(final_score, 2),
            "matched_skills": ", ".join(matched),
            "missing_must_have": ", ".join(missing),
            "experience_years": years,
            "experience_gap": round(max(minimum_years - years, 0), 1),
            "decision": decision,
            "error": "",
            "similarity_score": round(similarity_score, 2),
            "skill_coverage": round(skill_coverage, 2),
            "experience_score": round(experience_score, 2),
            "nice_to_have_matches": ", ".join(nice_matches),
        })
        valid_index += 1

    return pd.DataFrame(rows).sort_values(
        ["match_score", "candidate"], ascending=[False, True]
    ).reset_index(drop=True)
