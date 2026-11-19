from pathlib import Path

from backend.app.screening import score_resumes


def test_demo_ranking(tmp_path: Path) -> None:
    (tmp_path / "strong.txt").write_text(
        "Python SQL Pandas machine learning 3 years",
        encoding="utf-8",
    )
    (tmp_path / "weak.txt").write_text(
        "Java React 1 year",
        encoding="utf-8",
    )

    result = score_resumes(
        str(tmp_path),
        "Data analyst Python SQL Pandas machine learning 2 years",
        ["python", "sql", "pandas", "machine learning"],
        minimum_years=2,
        shortlist_threshold=50,
    )

    assert len(result) == 2
    assert result.iloc[0]["candidate"] == "strong"
    assert result.iloc[0]["decision"] == "Shortlist"


def test_custom_weights_and_nice_to_have(tmp_path: Path) -> None:
    (tmp_path / "profile.txt").write_text(
        "Python SQL Docker 5 years",
        encoding="utf-8",
    )
    result = score_resumes(
        str(tmp_path),
        "Python SQL Docker",
        ["python", "sql"],
        minimum_years=5,
        shortlist_threshold=40,
        nice_to_have_skills=["docker"],
        weights={
            "similarity": 20,
            "skills": 70,
            "experience": 10,
        },
    )
    row = result.iloc[0]
    assert row["match_score"] <= 100
    assert row["nice_to_have_matches"] == "docker"
    assert row["similarity_score"] >= 0
