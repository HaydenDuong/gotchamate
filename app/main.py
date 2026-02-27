"""FastAPI web application for the Discharge Intelligence Engine."""

import os
import shutil
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from pipeline.pipeline import run_pipeline
from pipeline.store import list_summaries, load_summary, delete_summary

load_dotenv()

DB_PATH = Path("data/snapshots.db")
DEMO_USER = os.environ.get("DEMO_USER", "demo")
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "demo123")
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-to-a-long-random-string")

app = FastAPI(title="Discharge Intelligence Engine")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

templates = Jinja2Templates(directory="templates")


# ── Auth helpers ──────────────────────────────────────────────────────────────

def is_logged_in(request: Request) -> bool:
    return request.session.get("logged_in") is True


def require_login(request: Request):
    """Return a redirect response if not logged in, else None."""
    if not is_logged_in(request):
        return RedirectResponse("/login", status_code=302)
    return None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if is_logged_in(request):
        return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if is_logged_in(request):
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == DEMO_USER and password == DEMO_PASSWORD:
        request.session["logged_in"] = True
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid username or password."}
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if redir := require_login(request):
        return redir
    summaries = list_summaries(DB_PATH)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "summaries": summaries, "error": None},
    )


@app.post("/upload", response_class=HTMLResponse)
async def upload_pdf(request: Request, pdf_file: UploadFile = File(...)):
    if redir := require_login(request):
        return redir

    if not pdf_file.filename or not pdf_file.filename.lower().endswith(".pdf"):
        summaries = list_summaries(DB_PATH)
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "summaries": summaries, "error": "Please upload a PDF file."},
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(pdf_file.file, tmp)
        tmp_path = tmp.name

    try:
        summary = run_pipeline(tmp_path, save_to_db=True, db_path=DB_PATH)
    except ValueError as e:
        summaries = list_summaries(DB_PATH)
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "summaries": summaries, "error": f"Extraction failed: {e}"},
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    # Get the id of the row we just inserted (latest)
    rows = list_summaries(DB_PATH)
    latest_id = rows[0]["id"] if rows else 1
    return RedirectResponse(f"/summary/{latest_id}", status_code=302)


@app.post("/delete/{summary_id}")
async def delete_summary_route(request: Request, summary_id: int):
    if redir := require_login(request):
        return redir
    delete_summary(DB_PATH, summary_id)
    return RedirectResponse("/dashboard", status_code=302)


@app.get("/summary/{summary_id}", response_class=HTMLResponse)
async def summary_detail(request: Request, summary_id: int):
    if redir := require_login(request):
        return redir
    summary = load_summary(DB_PATH, summary_id)
    if summary is None:
        return HTMLResponse("<h2>Summary not found.</h2>", status_code=404)
    return templates.TemplateResponse(
        "summary.html",
        {"request": request, "summary": summary, "summary_id": summary_id},
    )
