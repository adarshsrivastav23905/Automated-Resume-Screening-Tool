import argparse
from pathlib import Path

from backend.app.screening import score_resumes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automated Resume Screening Tool")
    parser.add_argument("--resumes", default="resumes", help="Resume directory")
    parser.add_argument("--job", default="data/job_description.txt", help="Job description file")
    parser.add_argument("--minimum-years", type=float, default=2.0)
    parser.add_argument("--threshold", type=float, default=50.0)
    parser.add_argument("--output", default="outputs/ranking_report.csv")
    parser.add_argument(
        "--must-have",
        nargs="+",
        default=["python", "sql", "pandas", "machine learning"],
    )
    parser.add_argument("--nice-to-have", nargs="*", default=["scikit-learn", "tableau"])
    parser.add_argument("--similarity-weight", type=float, default=55)
    parser.add_argument("--skill-weight", type=float, default=35)
    parser.add_argument("--experience-weight", type=float, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    job_description = Path(args.job).read_text(encoding="utf-8")
    results = score_resumes(
        resume_directory=args.resumes,
        job_description=job_description,
        must_have_skills=args.must_have,
        minimum_years=args.minimum_years,
        shortlist_threshold=args.threshold,
        nice_to_have_skills=args.nice_to_have,
        weights={
            "similarity": args.similarity_weight,
            "skills": args.skill_weight,
            "experience": args.experience_weight,
        },
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)

    print("\nResume Screening Results")
    print("=" * 80)
    print(results.to_string(index=False))
    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
