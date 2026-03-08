import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/data/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="TrustDevis API", version="0.1.0")

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")


def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS estimates (
            id UUID PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL,
            sector TEXT NOT NULL,
            country TEXT NOT NULL,
            region_code TEXT NOT NULL,
            consent_training BOOLEAN NOT NULL,
            original_filename TEXT,
            storage_path TEXT NOT NULL
        );
        """))

@app.on_event("startup")
def _startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/health")
def health():
    return {"ok": True, "ts": datetime.utcnow().isoformat()}


@app.post("/api/v1/estimate/upload")
async def upload_estimate(
    file: UploadFile = File(...),
    sector: str = Form(...),
    country: str = Form(...),
    region_code: str = Form(...),
    consent_training: bool = Form(...),
    email: Optional[str] = Form(None),
):
    # Minimal validation
    if country not in {"FR", "BE", "LU"}:
        raise HTTPException(status_code=400, detail="country must be FR|BE|LU")
    if not sector:
        raise HTTPException(status_code=400, detail="sector required")

    estimate_id = uuid.uuid4()
    safe_name = f"{estimate_id}_{os.path.basename(file.filename)}"
    out_path = os.path.join(UPLOAD_DIR, safe_name)

    content = await file.read()
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="file too large (max 15MB)")

    with open(out_path, "wb") as f:
        f.write(content)

    with engine.begin() as conn:
        conn.execute(
            text("""
            INSERT INTO estimates (id, created_at, sector, country, region_code, consent_training, original_filename, storage_path)
            VALUES (:id, NOW(), :sector, :country, :region_code, :consent_training, :original_filename, :storage_path)
            """),
            {
                "id": str(estimate_id),
                "sector": sector,
                "country": country,
                "region_code": region_code,
                "consent_training": consent_training,
                "original_filename": file.filename,
                "storage_path": out_path,
            },
        )

    return {"estimate_id": str(estimate_id), "stored": True}

