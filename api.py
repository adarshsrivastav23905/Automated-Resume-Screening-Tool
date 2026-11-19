import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from src.screening import score_resumes


app = FastAPI(
    title="HireLens Screening API",
    description="Automated resume screening service for future ATS integrations.",
    version="2.2",
)


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "service": "HireLens Screening API"}


@app.post("/screen")
async def screen_resumes(
    job_description: str = Form(...),
    must_have: str = Form("python, sql"),
    nice_to_have: str = Form(""),
    minimum_years: float = Form(2.0),
    threshold: float = Form(50.0),
    files: list[UploadFile] = File(...),
) -> JSONResponse:
    must_have_skills = [skill.strip() for skill in must_have.split(",") if skill.strip()]
    nice_to_have_skills = [skill.strip() for skill in nice_to_have.split(",") if skill.strip()]

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        for uploaded in files:
            if not uploaded.filename:
                continue
            suffix = Path(uploaded.filename).suffix.lower()
            if suffix not in {".txt", ".pdf", ".docx"}:
                continue
            destination = temp_path / uploaded.filename
            destination.write_bytes(await uploaded.read())

        results = score_resumes(
            resume_directory=temp_dir,
            job_description=job_description,
            must_have_skills=must_have_skills,
            minimum_years=minimum_years,
            shortlist_threshold=threshold,
            nice_to_have_skills=nice_to_have_skills,
        )

    return JSONResponse(content=results.to_dict(orient="records"))
