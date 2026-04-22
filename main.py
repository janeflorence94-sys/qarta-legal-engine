import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from docx_builder import build_outputs
from pipeline import adapt_contract

OUTPUTS_DIR = Path(__file__).parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".docx", ".pdf"}

app = FastAPI(
    title="Qarta Legal Engine",
    description="CN → SG contract localisation pipeline",
    version="1.0.0",
)


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

    try:
        result = adapt_contract(
            file_bytes=file_bytes,
            file_ext=suffix.lstrip("."),
            corridor=corridor,
            doc_type=doc_type,
            company_name=company_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))

    try:
        paths = build_outputs(
            clean_text=result["clean"],
            redline_text=result["redline"],
            commentary_text=result["commentary"],
            company_name=company_name,
            doc_type=doc_type,
            output_dir=str(OUTPUTS_DIR),
            job_id=job_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document build failed: {e}")

    return JSONResponse({
        "status": "success",
        "job_id": job_id,
        "files": {
            "clean":      f"/outputs/{job_id}_clean.docx",
            "redline":    f"/outputs/{job_id}_redline.docx",
            "commentary": f"/outputs/{job_id}_commentary.docx",
        },
        "metadata": {
            "company":        company_name,
            "corridor":       corridor,
            "doc_type":       doc_type,
            "source_file":    file.filename,
            "records_loaded": result.get("records_loaded", 0),
            "timestamp":      datetime.now(timezone.utc).isoformat(),
        },
    })


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
