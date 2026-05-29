import json
import os
import re
import smtplib
import sys
import threading
import traceback
import uuid
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from docx_builder import build_outputs
from pipeline import adapt_contract

# Both output .docx files and status JSON live together in /tmp/outputs/
OUTPUTS_DIR = Path("/tmp/outputs")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".docx", ".pdf"}


# ── File-based job store (/tmp/outputs/{job_id}_status.json) ──────────────────

def _status_path(job_id: str) -> Path:
    return OUTPUTS_DIR / f"{job_id}_status.json"


def _output_files(job_id: str) -> dict:
    return {
        "clean":      f"/outputs/{job_id}_clean.docx",
        "redline":    f"/outputs/{job_id}_redline.docx",
        "commentary": f"/outputs/{job_id}_commentary.docx",
    }


def _outputs_exist(job_id: str) -> bool:
    return all(
        (OUTPUTS_DIR / f"{job_id}_{suffix}.docx").exists()
        for suffix in ("clean", "redline", "commentary")
    )


def _write_status(job_id: str, data: dict) -> None:
    _status_path(job_id).write_text(json.dumps(data), encoding="utf-8")


def _read_status(job_id: str) -> dict | None:
    path = _status_path(job_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _update_status(job_id: str, updates: dict) -> None:
    data = _read_status(job_id) or {"job_id": job_id}
    data.update(updates)
    _write_status(job_id, data)


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
    print(f"OUTPUTS_DIR: {OUTPUTS_DIR} (exists={OUTPUTS_DIR.exists()})")
    print("=== END ENV CHECK ===")


# ── Clause counter ────────────────────────────────────────────────────────────

def _count_clauses(commentary_text: str) -> int:
    """Count distinct clause rule IDs that fired, parsed from commentary output."""
    if not commentary_text:
        return 0
    # Match patterns like STR-001, EMP-SG-014, RULE-2, PDPA-003, JV-007, etc.
    ids = re.findall(r'\b(?:STR|EMP|RULE|PDPA|CPF|TAX|IP|NDA|JV|SHA)-[A-Z0-9\-]+', commentary_text)
    return len(set(ids))  # distinct count only


# ── Background worker ──────────────────────────────────────────────────────────

def _run_pipeline(
    job_id: str,
    file_bytes: bytes,
    file_ext: str,
    corridor: str,
    doc_type: str,
    company_name: str,
    source_filename: str,
    deal_profile: dict = None,
):
    """Runs in a background thread. Writes status to /tmp/outputs/{job_id}_status.json."""
    print(f"[job {job_id}] Pipeline started.", flush=True)
    try:
        result = adapt_contract(
            file_bytes=file_bytes,
            file_ext=file_ext,
            corridor=corridor,
            doc_type=doc_type,
            company_name=company_name,
            deal_profile=deal_profile or {},
        )

        clause_count = _count_clauses(result.get("commentary", ""))

        build_outputs(
            clean_text=result["clean"],
            redline_text=result["redline"],
            commentary_text=result["commentary"],
            company_name=company_name,
            doc_type=doc_type,
            output_dir=str(OUTPUTS_DIR),
            job_id=job_id,
            corridor=corridor,
        )

        _update_status(job_id, {
            "status": "complete",
            "files": _output_files(job_id),
            "clause_count_adapted": clause_count,
            "metadata": {
                "company":        company_name,
                "corridor":       corridor,
                "doc_type":       doc_type,
                "source_file":    source_filename,
                "records_loaded": result.get("records_loaded", 0),
                "completed_at":   datetime.now(timezone.utc).isoformat(),
            },
        })
        print(f"[job {job_id}] Complete.", flush=True)

    except Exception as e:
        tb = traceback.format_exc()
        print(f"[PIPELINE ERROR] job_id={job_id}\n{tb}", flush=True)
        _update_status(job_id, {"status": "error", "error": f"{str(e)}\n{tb}"})


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/debug/env")
def debug_env():
    return dict(os.environ)


@app.get("/test/nda")
def test_nda():
    import requests
    key  = os.getenv("AIRTABLE_API_KEY")
    base = os.getenv("AIRTABLE_BASE_ID")
    url  = f"https://api.airtable.com/v0/{base}/NDA%20Clauses%20%28Demo%20Tier%29?maxRecords=1"
    r = requests.get(url, headers={"Authorization": f"Bearer {key}"})
    return {
        "status_code": r.status_code,
        "response":    r.text[:500],
        "key_prefix":  key[:15] if key else "MISSING",
        "base_id":     base or "MISSING",
        "url":         url,
    }


@app.post("/adapt")
async def adapt(
    file: UploadFile = File(...),
    corridor: str = Form(...),
    doc_type: str = Form(...),
    company_name: str = Form(...),
    deal_profile: str = Form(default="{}"),
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

    try:
        deal_profile_dict = json.loads(deal_profile) if deal_profile else {}
    except (json.JSONDecodeError, TypeError):
        deal_profile_dict = {}

    job_id = str(uuid.uuid4())

    _write_status(job_id, {
        "status":       "processing",
        "job_id":       job_id,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    })

    thread = threading.Thread(
        target=_run_pipeline,
        args=(job_id, file_bytes, suffix.lstrip("."), corridor, doc_type, company_name, file.filename, deal_profile_dict),
        daemon=True,
    )
    thread.start()
    sys.stdout.flush()

    return JSONResponse(
        status_code=202,
        content={"status": "processing", "job_id": job_id},
    )


@app.get("/status/{job_id}")
def status(job_id: str):
    # 1. Output files exist → job is complete regardless of status file
    if _outputs_exist(job_id):
        # Refresh status file so it reflects reality after a redeploy
        stored = _read_status(job_id) or {}
        if stored.get("status") != "complete":
            _update_status(job_id, {
                "status": "complete",
                "files":  _output_files(job_id),
                "recovered_after_redeploy": True,
            })
        return JSONResponse(_read_status(job_id))

    # 2. Status file exists (processing or error)
    stored = _read_status(job_id)
    if stored:
        return JSONResponse(stored)

    # 3. Neither exists
    raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")


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


# ── Attorney email ─────────────────────────────────────────────────────────────

class AttorneyEmailRequest(BaseModel):
    attorney_email: str
    job_id: str
    document_urls: List[str]


@app.post("/send-attorney")
def send_attorney(req: AttorneyEmailRequest):
    smtp_email    = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_email or not smtp_password:
        raise HTTPException(
            status_code=500,
            detail="SMTP credentials are not configured on the server.",
        )

    if "@" not in req.attorney_email or "." not in req.attorney_email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Invalid attorney_email address.")

    if len(req.document_urls) != 3:
        raise HTTPException(
            status_code=400,
            detail="Exactly 3 document URLs are required (clean, redline, commentary).",
        )

    labels = ["Clean Version", "Redline Version", "Commentary"]
    doc_lines = "\n".join(
        f"  {i+1}. {label}:\n     {url}"
        for i, (label, url) in enumerate(zip(labels, req.document_urls))
    )

    body = f"""\
Dear Attorney,

Please find below the download links for the adapted legal documents prepared by Qarta Legal for your review.

Job Reference: {req.job_id}
Prepared:      {datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC")}

─────────────────────────────────────────
DOCUMENT DOWNLOAD LINKS (valid for 1 hour)
─────────────────────────────────────────
{doc_lines}

─────────────────────────────────────────

These documents have been localised by the Qarta Legal engine and are provided for attorney review prior to execution. Please do not reply to this email directly.

For queries, contact the Qarta team via your client portal.

Regards,
Qarta Legal
"""

    msg = MIMEMultipart()
    msg["From"]    = smtp_email
    msg["To"]      = req.attorney_email
    msg["Subject"] = f"Legal Documents for Review — Qarta Legal [{req.job_id}]"
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, req.attorney_email, msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(
            status_code=500,
            detail="SMTP authentication failed. Check SMTP_EMAIL and SMTP_PASSWORD.",
        )
    except smtplib.SMTPException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")

    return {"status": "sent", "recipient": req.attorney_email, "job_id": req.job_id}
