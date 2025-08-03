from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.core.schemas.resume_source import ResumeSource
from src.core.schemas.job_posting import JobPosting
from src.core.services.resume_maker.source import upload_resume
from src.core.database.resume_sources import (
    get_resume_sources_by_user, 
    get_resume_source_by_id,
    get_resume_source_content_by_id
)
from src.core.services.resume_maker.workflow import run_resume_maker
from src.core.services.job_search.workflow import run_job_search_workflow
from src.core.database.job_postings import get_latest_job_postings
from src.core.services.job_analysis.workflow import run_job_analysis

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/users/{user_id}/resume-sources")
async def upload_resume_source_api(user_id: str, file: UploadFile = File(...)):
    """
    Uploads a resume source file for a user.
    """
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    resume_source = await upload_resume(file_path, user_id)
    return {
        "filename": file.filename, 
        "resume_source_id": resume_source.id,
        "original_file_name": resume_source.original_file_name
    }

@app.get("/users/{user_id}/resume-sources/{resume_source_id}")
async def get_resume_api(user_id: str, resume_source_id: int):
    """
    Retrieves a specific resume source for a user.
    """
    resume_source = get_resume_source_by_id(resume_source_id)
    if not resume_source or resume_source.user_id != user_id:
        raise HTTPException(status_code=404, detail="Resume source not found")
    return resume_source

@app.get("/users/{user_id}/resume-sources/{resume_source_id}/content")
async def get_resume_content_api(user_id: str, resume_source_id: int):
    """
    Retrieves the content of a specific resume source for a user.
    """
    resume_source = get_resume_source_by_id(resume_source_id)
    if not resume_source or resume_source.user_id != user_id:
        raise HTTPException(status_code=404, detail="Resume source not found")
    
    content = get_resume_source_content_by_id(resume_source_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Resume content not found")
    
    return {
        "id": resume_source.id,
        "original_file_name": resume_source.original_file_name,
        "content": content
    }

@app.get("/users/{user_id}/resume-sources", response_model=List[ResumeSource])
async def get_resume_sources_api(user_id: str):
    """
    Retrieves all resume sources for a user.
    """
    return get_resume_sources_by_user(user_id)

@app.post("/users/{user_id}/resumes")
async def make_resume_api(user_id: str, job_target: str):
    """
    Creates a resume for a user based on a job target.
    """
    resume_path = await run_resume_maker(job_target, user_id)
    return {"resume_path": resume_path}

@app.post("/users/{user_id}/job-postings")
async def find_job_postings_api(user_id: str):
    """
    Finds job postings for a user.
    """
    job_postings = await run_job_search_workflow(user_id)
    return {"job_postings": job_postings}

@app.get("/job-postings", response_model=List[JobPosting])
async def get_job_postings_api(limit: int = 10):
    """
    Retrieves the latest job postings.
    """
    return get_latest_job_postings(limit)

@app.post("/users/{user_id}/analyze-job")
async def analyze_job_and_resume_api(user_id: str):
    """
    Analyzes a job posting against a user's resume.
    """
    analysis_result = await run_job_analysis(user_id=user_id)
    return {"analysis_result": analysis_result}

@app.get("/analysis-result")
async def get_analysis_result_api():
    """
    Retrieves the result of a job analysis.
    """
    # This is a placeholder. You'll need to implement logic to store and retrieve
    # the analysis result.
    return {"message": "Analysis result not implemented yet."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)