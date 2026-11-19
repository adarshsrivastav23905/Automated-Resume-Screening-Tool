# Automated Resume Screening Tool

An explainable Python/NLP project that extracts text from TXT, PDF, and DOCX resumes, compares candidates with a job description, identifies must-have skill gaps, ranks candidates, and exports a CSV report.

> **Important:** This is a student proof-of-work tool using synthetic data. It supports shortlisting decisions but must not make final hiring decisions without human review.

## Features

- PDF, DOCX, and TXT text extraction
- Text cleaning and skill extraction
- TF-IDF vectorization and cosine similarity
- Must-have skill coverage and experience scoring
- Transparent weighted ranking
- CSV report generation
- Streamlit recruiter dashboard
- Downloadable ranking results
- Configurable scoring weights
- Nice-to-have skill bonuses
- Candidate and decision filters
- Score component analytics
- SQLite audit history
- CSV and JSON exports
- REST API for future ATS integrations

## Project structure

```text
Automated-Resume-Screening-Tool/
├── app.py
├── main.py
├── requirements.txt
├── data/
│   └── job_description.txt
├── resumes/
├── src/
│   ├── text_processing.py
│   ├── skills.py
│   └── screening.py
├── outputs/
├── images/
├── docs/
└── tests/
```

## How it works

```text
Resumes + Job Description
           |
      Text Extraction
           |
      Text Cleaning
           |
    Skill + Experience Extraction
           |
TF-IDF + Cosine Similarity + Skill Rules
           |
 Weighted Score + Ranking
           |
Shortlist / Review / Reject + CSV Report
```

The final score is:

```text
55% TF-IDF similarity
+ 35% must-have skill coverage
+ 10% minimum-experience coverage
```

Candidates meeting the score threshold are marked **Shortlist**. Candidates meeting the score threshold but missing must-have skills are marked **Review**. Candidates below the threshold are marked **Reject**.

## Setup

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the CLI

```bash
python main.py
```

Override the defaults if needed:

```bash
python main.py --minimum-years 2 --threshold 50 --output outputs/ranking_report.csv
```

The CLI reads `data/job_description.txt` and scans `resumes/`, then creates `outputs/ranking_report.csv`.

## Run the dashboard

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, paste or edit a job description, upload resumes, and rank candidates.

## Run the REST API

```bash
uvicorn api:app --reload
```

Open `http://localhost:8000/docs` for the Swagger interface.

## Run tests

```bash
python -m pytest -q
```

## Tech stack

Python, Pandas, NumPy, Scikit-learn, TF-IDF, cosine similarity, Regex, pdfplumber, python-docx, and Streamlit.

## Ethical use

- Never use protected attributes or proxy data.
- Keep a recruiter in the final decision loop.
- Provide candidates with an appeal or review process.
- Collect only information necessary for screening.
- Validate ranking behavior on realistic, consented datasets.

## Resume screenshot and proof checklist

1. Project folder structure.
2. `resumes/` containing sample files.
3. Job description content.
4. Terminal output from `python main.py`.
5. Ranking table in the terminal.
6. Generated `outputs/ranking_report.csv`.
7. Streamlit dashboard before and after ranking.
8. GitHub repository preview.
