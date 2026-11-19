# Project proof checklist

Use synthetic or consented data only. Do not upload real resumes or personal information to a public repository.

## Screenshots

- [ ] `screenshots/01_dashboard.png` — HireLens dashboard before analysis.
- [ ] `screenshots/02_candidate_ranking.png` — candidate results with score and decision.
- [ ] `screenshots/03_candidate_evidence.png` — selected candidate's matched and missing skills.
- [ ] `screenshots/04_analytics.png` — score comparison and component analytics.
- [ ] `screenshots/05_api_docs.png` — FastAPI Swagger documentation.
- [ ] `screenshots/06_csv_report.png` — generated CSV report.
- [ ] `screenshots/07_repository.png` — GitHub repository overview and folder layout.

## Demonstration sequence

1. Start the dashboard and show its configured job description and settings.
2. Upload the sample resumes and run screening.
3. Filter and search candidates, then select a row to inspect evidence.
4. Open analytics and compare candidate scores.
5. Download CSV and JSON reports.
6. Open `/docs`, run the API health check, and submit one sample resume.
7. Run `python -m pytest -q` and show the passing tests.

## Portfolio notes

- Explain the score components and their configurable weights.
- Explain the limitations of TF-IDF and heuristic experience extraction.
- Emphasize that the system supports human review rather than making hiring decisions.
