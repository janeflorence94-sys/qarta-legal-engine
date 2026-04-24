import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from docx_builder import build_outputs
from pipeline import adapt_contract

OUTPUTS_DIR = Path(__file__).parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

JOBS_DIR = Path("/tmp/jobs")
JOBS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".docx", ".pdf"}


# ── File-based job store ───────────────────────────────────────────────────────

def _job_path(job_id: str) -> Path:
    return JOBS_DIR / f"{job_id}.json"


def _write_job(data: dict) -> None:
    _job_path(data["job_id"]).write_text(json.dumps(data), encoding="utf-8")


def _read_job(job_id: str) -> dict | None:
    path = _job_path(job_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _update_job(job_id: str, updates: dict) -> None:
    data = _read_job(job_id) or {"job_id": job_id}
    data.update(updates)
    _write_job(data)

app = FastAPI(
    title="Qarta Legal Engine",
    description="CN → SG contract localisation pipeline",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup ────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    print("=== STARTUP ENV CHECK ===")
    print(f"ANTHROPIC_API_KEY: {'SET' if os.getenv('ANTHROPIC_API_KEY') else 'MISSING'}")
    print(f"AIRTABLE_API_KEY:  {'SET' if os.getenv('AIRTABLE_API_KEY')  else 'MISSING'}")
    print(f"AIRTABLE_BASE_ID:  {'SET' if os.getenv('AIRTABLE_BASE_ID')  else 'MISSING'}")
    print(f"Total env vars: {len(os.environ)}")
    print("=== END ENV CHECK ===")


# ── Background worker ──────────────────────────────────────────────────────────

def _run_pipeline(
    job_id: str,
    file_bytes: bytes,
    file_ext: str,
    corridor: str,
    doc_type: str,
    company_name: str,
    source_filename: str,
):
    """Runs in a background thread. Writes status to /tmp/jobs/{job_id}.json."""
    print(f"[job {job_id}] Pipeline started.")
    try:
        result = adapt_contract(
            file_bytes=file_bytes,
            file_ext=file_ext,
            corridor=corridor,
            doc_type=doc_type,
            company_name=company_name,
        )

        build_outputs(
            clean_text=result["clean"],
            redline_text=result["redline"],
            commentary_text=result["commentary"],
            company_name=company_name,
            doc_type=doc_type,
            output_dir=str(OUTPUTS_DIR),
            job_id=job_id,
        )

        _update_job(job_id, {
            "status": "complete",
            "files": {
                "clean":      f"/outputs/{job_id}_clean.docx",
                "redline":    f"/outputs/{job_id}_redline.docx",
                "commentary": f"/outputs/{job_id}_commentary.docx",
            },
            "metadata": {
                "company":        company_name,
                "corridor":       corridor,
                "doc_type":       doc_type,
                "source_file":    source_filename,
                "records_loaded": result.get("records_loaded", 0),
                "completed_at":   datetime.now(timezone.utc).isoformat(),
            },
        })
        print(f"[job {job_id}] Complete.")

    except Exception as e:
        _update_job(job_id, {"status": "error", "error": str(e)})
        print(f"[job {job_id}] Error: {e}")


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/debug/env")
def debug_env():
    return dict(os.environ)


@app.post("/adapt")
async def adapt(
    file: UploadFile = File(...),
    corridor: str = Form(...),
    doc_type: str = Form(...),
    company_name: str = Form(...),
):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Only .docx and .pdf are accepted.",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    job_id = str(uuid.uuid4())

    # Write initial job state before thread starts
    _write_job({
        "status":       "processing",
        "job_id":       job_id,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    })

    thread = threading.Thread(
        target=_run_pipeline,
        args=(job_id, file_bytes, suffix.lstrip("."), corridor, doc_type, company_name, file.filename),
        daemon=True,
    )
    thread.start()

    return JSONResponse(
        status_code=202,
        content={"status": "processing", "job_id": job_id},
    )


@app.get("/status/{job_id}")
def status(job_id: str):
    job = _read_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return JSONResponse(job)


@app.get("/outputs/{filename}")
def serve_output(filename: str):
    if not filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are served from this endpoint.")

    file_path = OUTPUTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")

    try:
        file_path.resolve().relative_to(OUTPUTS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file path.")

    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )
