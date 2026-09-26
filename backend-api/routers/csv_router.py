import os
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from services.csv_analysis import (
    JOBS,
    JOBS_LOCK,
    analyze_csv,
    save_upload,
)


router = APIRouter(
    prefix="/api/transaction",
    tags=["CSV Transaction Analysis"],
)

UPLOAD_ROOT = Path("temp/csv_jobs")
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)


@router.post("/analyze-csv", status_code=202)
async def analyze_csv_upload(
    background_tasks: BackgroundTasks,
    transaction_file: UploadFile = File(...),
    identity_file: UploadFile | None = File(None),
):
    if not transaction_file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Transaction file must be a CSV.",
        )

    if (
        identity_file
        and not identity_file.filename.lower().endswith(".csv")
    ):
        raise HTTPException(
            status_code=400,
            detail="Identity file must be a CSV.",
        )

    job_id = uuid.uuid4().hex
    job_dir = UPLOAD_ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    transaction_path = job_dir / "transaction.csv"
    identity_path = (
        job_dir / "identity.csv"
        if identity_file
        else None
    )
    result_path = job_dir / "analysis_result.csv"

    save_upload(
        transaction_file,
        transaction_path,
    )

    if identity_file:
        save_upload(
            identity_file,
            identity_path,
        )

    with JOBS_LOCK:
        JOBS[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "processed_rows": 0,
            "total_rows": 0,
            "message": "Waiting for analysis...",
        }

    background_tasks.add_task(
        analyze_csv,
        job_id,
        str(transaction_path),
        str(identity_path) if identity_path else None,
        str(result_path),
    )

    return {
        "job_id": job_id,
        "status": "queued",
    }


@router.get("/analyze-csv/{job_id}")
def get_csv_analysis(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Analysis job not found.",
        )

    response = dict(job)
    response.pop("result_path", None)

    return response


@router.get("/analyze-csv/{job_id}/download")
def download_csv_analysis(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Analysis job not found.",
        )

    if job.get("status") != "completed":
        raise HTTPException(
            status_code=409,
            detail="Analysis is not completed yet.",
        )

    result_path = job.get("result_path")

    if not result_path or not os.path.exists(result_path):
        raise HTTPException(
            status_code=404,
            detail="Result file not found.",
        )

    return FileResponse(
        result_path,
        media_type="text/csv",
        filename="fraud_analysis_result.csv",
    )
