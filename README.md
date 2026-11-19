# Automated Resume Screening Tool

> An explainable resume screening platform with a Streamlit recruiter workspace, a FastAPI service, configurable scoring, candidate evidence, and saved screening history.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC)

This student-built portfolio project uses synthetic resumes and sample job descriptions. It is a decision-support demo, not an automated hiring decision maker.

---

## Key features

- **Multi-format ingestion:** Extract content from TXT, PDF, and DOCX resumes.
- **Hybrid relevance scoring:** Combine TF-IDF/cosine similarity with explicit skill and experience rules.
- **Configurable scoring:** Adjust similarity, must-have coverage, and experience weights.
- **Must-have gap detection:** Clearly show matched and missing requirements.
- **Nice-to-have signals:** Apply a small, capped score bonus for optional skills.
- **Recruiter workspace:** Filter, search, review evidence, and explore score analytics in Streamlit.
- **Reusable API:** Submit resumes for screening through FastAPI and inspect the API through Swagger UI.
- **Screening history:** Store prior run settings and result snapshots in a local SQLite audit database.
- **Portable reports:** Export CSV and JSON reports.
- **Human-in-the-loop:** Candidates missing must-have skills are flagged for review rather than silently treated as a match.

## System architecture

```text
                         ┌─────────────────────────┐
                         │   Job description + JD  │
                         │   must/nice-to-have     │
                         └────────────┬────────────┘
                                      │
┌──────────────────────┐    ┌────────▼────────────┐
│ Streamlit recruiter  │───▶│ Backend screening   │◀─── FastAPI clients
│ workspace            │    │ pipeline            │     (REST / JSON)
└──────────────────────┘    └────────┬────────────┘
                                      │
                  ┌───────────────────┼────────────────────┐
                  ▼                   ▼                    ▼
          TXT/PDF/DOCX         TF-IDF + rules       SQLite run history
          text extraction      score + reasons      CSV / JSON exports
```

### Screening workflow

1. Provide a job description, required skills, and optional skills.
2. Upload resumes in TXT, PDF, or DOCX format.
3. Extract and normalize resume text.
4. Detect skills and estimate experience from text.
5. Compute similarity, must-have coverage, and experience coverage.
6. Rank candidates and label them **Shortlist**, **Review**, or **Reject**.
7. Review evidence, inspect analytics, and export reports.

### Score model

The default score is a weighted combination of:

```text
Final score = similarity weight × TF-IDF similarity
            + skills weight × must-have coverage
            + experience weight × experience coverage
            + capped nice-to-have bonus
```

Default weights are 55% similarity, 35% must-have coverage, and 10% experience coverage. The three weights are normalized automatically. The optional-skill bonus is capped at five points. A candidate who meets the score threshold but is missing a must-have skill is marked **Review**, not **Shortlist**.

> The current years-of-experience parser is a lightweight heuristic. Its estimate should be checked by a recruiter and is not a verified employment-history calculation.

## Project structure

```text
Automated-Resume-Screening-Tool/
├── backend/
│   ├── __init__.py
│   ├── api.py                 # FastAPI endpoints
│   ├── cli.py                 # Command-line runner
│   └── app/
│       ├── __init__.py
│       ├── audit_store.py     # SQLite run history
│       ├── screening.py       # Scoring and ranking pipeline
│       ├── skills.py          # Skill and experience extraction
│       └── text_processing.py # TXT, PDF, DOCX and text cleaning
├── frontend/
│   ├── __init__.py
│   └── app.py                 # Streamlit recruiter dashboard
├── data/
│   └── job_description.txt
├── resumes/                   # Synthetic sample resumes
├── outputs/                   # Generated CSV and local SQLite history
├── screenshots/               # Add project demonstration screenshots
├── docs/                       # Supporting project documentation
├── tests/
│   └── test_pipeline.py
├── .streamlit/
│   └── config.toml
├── .gitignore
├── requirements.txt
└── README.md
```

## Screenshots

Add your own verified captures to `screenshots/` and link them here when ready. The [proof checklist](docs/PROOF_CHECKLIST.md) has the recommended demo sequence. Suggested captures:

| Suggested file | What to capture |
|---|---|
| `01_dashboard.png` | Recruiter workspace before screening |
| `02_candidate_ranking.png` | Ranked candidate list with score and decision |
| `03_candidate_evidence.png` | Matched and missing skill evidence |
| `04_analytics.png` | Candidate score analytics |
| `05_api_docs.png` | FastAPI Swagger documentation |
| `06_csv_report.png` | Generated report opened in a spreadsheet |

## Quick start

### Prerequisites

- Python 3.10 or later
- Windows PowerShell, macOS Terminal, or Linux shell

### Install

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run commands from the repository root.

### Start the Streamlit dashboard

```bash
streamlit run frontend/app.py
```

Open the local URL printed by Streamlit. The sample job description is preloaded; upload resumes and choose screening settings in the sidebar.

### Run the command-line screening

```bash
python -m backend.cli
```

The default command reads `data/job_description.txt`, screens files in `resumes/`, and writes `outputs/ranking_report.csv`.

Customize the job, resume folder, weights, and threshold:

**Windows PowerShell**

```powershell
python -m backend.cli `
  --job data/job_description.txt `
  --resumes resumes `
  --must-have python sql pandas `
  --nice-to-have tableau scikit-learn `
  --minimum-years 2 `
  --threshold 50 `
  --similarity-weight 55 `
  --skill-weight 35 `
  --experience-weight 10 `
  --output outputs/ranking_report.csv
```

**macOS/Linux**

```bash
python -m backend.cli \
  --job data/job_description.txt \
  --resumes resumes \
  --must-have python sql pandas \
  --nice-to-have tableau scikit-learn \
  --minimum-years 2 \
  --threshold 50 \
  --similarity-weight 55 \
  --skill-weight 35 \
  --experience-weight 10 \
  --output outputs/ranking_report.csv
```

### Start the REST API

```bash
uvicorn backend.api:app --reload
```

- Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

## API overview

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/health` | Check API availability |
| `POST` | `/screen` | Upload resumes and receive ranked screening results |

`POST /screen` accepts multipart form fields: `job_description`, comma-separated `must_have`, comma-separated `nice_to_have`, `minimum_years`, `threshold`, and one or more files. Supported file types are TXT, PDF, and DOCX.

Example request using `curl`:

```bash
curl -X POST http://localhost:8000/screen \
  -F "job_description=Data analyst with Python and SQL" \
  -F "must_have=python,sql,pandas" \
  -F "nice_to_have=tableau" \
  -F "minimum_years=2" \
  -F "threshold=50" \
  -F "files=@resumes/Aarav_Sharma.txt"
```

The API currently returns results for each request and does not persist uploaded resume files. Run-history persistence is provided by the Streamlit workflow's SQLite audit store.

## Sample data and outputs

The repository includes four synthetic TXT resumes and a sample Data Analyst job description. After running the CLI:

- `outputs/ranking_report.csv` contains candidate scores, decisions, skill gaps, and score components.
- The Streamlit workspace can export a CSV or JSON report.
- `outputs/screening_history.db` is created locally by dashboard screenings and is excluded from Git.

All sample profiles are fictional and for demonstration only.

## Testing

Run the automated screening tests from the project root:

```bash
python -m pytest -q
```

The tests cover ranking behavior, custom weight handling, and nice-to-have skill matches.

## Future roadmap

- Better structured experience extraction from employment date ranges.
- Add tests for PDF/DOCX files and the FastAPI endpoints.
- Add candidate profile fields and configurable skill dictionaries.
- Add database migrations and PostgreSQL for multi-user deployments.
- Add authentication, authorization, and tenant isolation before exposing the API publicly.
- Add model versioning and evaluation against a consented, human-reviewed dataset.
- Add data retention controls and explicit deletion workflows.
- Add background processing for large resume batches.

## Deployment considerations

For a portfolio deployment, host the Streamlit dashboard and FastAPI service as separate Python services and configure the dashboard to call the deployed API only after adding an API-client layer. The current dashboard uses the local screening package directly, so it is designed for a single repository/runtime.

Before deploying publicly, add authentication and authorization, validate and limit uploads, configure CORS and HTTPS, use managed persistent storage for screening history, and provide data retention/deletion controls. The current API is an unauthenticated demo and must not be exposed as a production hiring service.

## Privacy, fairness, and production limitations

- Do not use protected attributes such as age, race, religion, caste, or gender for screening.
- Do not treat similarity scores as objective measures of candidate quality.
- Keep a qualified human reviewer responsible for decisions and provide a review path.
- Use synthetic or consented resumes only; avoid committing personal data or real resumes.
- The local SQLite history stores job descriptions and result snapshots. Review and remove local history as appropriate.
- The API has no authentication or upload-size limits and is a development/demo service. Do not expose it publicly without adding security controls.
- SQLite is suitable for a local single-user demonstration, not concurrent multi-instance production.

## Interview walkthrough

1. **What problem does the project address?** It reduces repetitive resume-to-job-description comparison by producing a consistent, inspectable first-pass ranking.
2. **How does the matching work?** TF-IDF converts text into weighted terms; cosine similarity compares resume and job-description vectors.
3. **Why combine text similarity and skill rules?** Similarity captures overlapping language, while explicit requirements make missing critical skills visible.
4. **How is the score calculated?** It combines configurable similarity, must-have coverage, and experience weights, with a small optional-skill bonus.
5. **How does the system handle a missing must-have?** It surfaces the gap and marks an otherwise high-scoring candidate for review.
6. **What are the parser's limitations?** Resume layouts vary; text extraction can fail, and the current experience estimate is a simple heuristic.
7. **Why provide both Streamlit and FastAPI?** Streamlit supports a quick interactive recruiter workflow; FastAPI exposes the core operation for other clients.
8. **What is stored in the screening history?** Screening inputs and the JSON snapshot of results are stored in the local SQLite database.
9. **How would you make this production-ready?** Add authentication, authorization, safe file handling, privacy and deletion controls, database migrations, monitoring, and human-reviewed evaluation.
10. **Can this system make hiring decisions?** No. It is a decision-support prototype; hiring decisions require qualified human review.

## License

No license has been selected for this repository yet. Add a `LICENSE` file before permitting reuse or redistribution.
