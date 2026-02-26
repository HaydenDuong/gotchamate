# Discharge Intelligence Engine

> AI-powered clinical document structuring — converts fragmented discharge summary PDFs into structured, actionable patient data in seconds.

**⚠️ Disclaimer:** This is a technical demonstration built for a hackathon. All outputs are AI-extracted and **require clinician verification**. This tool does not provide medical advice, diagnosis, or treatment recommendations.

---

## Overview

Transition of care after hospital discharge creates cognitive overload for GPs, caretakers, and elderly patients. Important medication changes and follow-up tasks are buried in narrative PDFs.

**Discharge Intelligence Engine** structures discharge summaries into workflow-ready clinical data — reducing information fragmentation and improving clarity.

### What it does

- Accepts uploaded discharge summary PDFs (text-based)
- Extracts raw text using **pdfplumber**
- Uses an **LLM** (Google Gemini or OpenAI) to convert unstructured text into structured JSON
- Validates output against a strict **Pydantic** schema
- Stores results in **SQLite**
- Displays a clean **Clinical Snapshot** dashboard

### What it extracts

| Field | Description |
|---|---|
| Patient name & age | From document header |
| Discharge date | If present in document |
| Active conditions | With active/historical status |
| Medications | Name, dose, frequency, and **change status** (New / Stopped / Dose Changed / Continuing) |
| Follow-ups | Specialty, timeframe, and **estimated due date** calculated from discharge date |
| Recent events | Admissions, discharges with dates and reasons |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| LLM | Google Gemini (free tier) or OpenAI |
| Validation | Pydantic v2 |
| PDF extraction | pdfplumber |
| Storage | SQLite |
| Frontend | Jinja2 templates + Tailwind CSS |

---

## Project Structure

```
gotchamate/
├── app/
│   └── main.py              # FastAPI routes and session auth
├── pipeline/
│   ├── models.py            # Pydantic data models
│   ├── extract_text.py      # PDF → raw text (pdfplumber)
│   ├── llm_extract.py       # Text → structured JSON (LLM)
│   ├── pipeline.py          # Orchestrator
│   └── store.py             # SQLite save / load / delete
├── templates/
│   ├── base.html            # Shared layout (Tailwind)
│   ├── login.html           # Login page
│   ├── dashboard.html       # Upload form + recent summaries
│   └── summary.html         # Clinical snapshot detail
├── pdf_samples/             # Synthetic demo PDFs
├── data/                    # SQLite database (auto-created)
├── create_sample_pdfs.py    # Generate demo PDFs
├── run_pipeline.py          # CLI entrypoint
├── requirements.txt
└── .env                     # API keys and config (not committed)
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- A Google Gemini API key (free tier) — [get one here](https://aistudio.google.com/app/apikey)
  — or an OpenAI API key

### 1. Clone the repository

```bash
git clone https://github.com/HaydenDuong/gotchamate.git
cd gotchamate
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
# LLM — choose one
GEMINI_API_KEY=your-gemini-key-here
GEMINI_MODEL=gemini-2.5-flash       # optional, this is the default

# OR
# OPENAI_API_KEY=sk-your-key-here
# OPENAI_MODEL=gpt-4o-mini

# Web app
DEMO_USER=demo
DEMO_PASSWORD=demo123
SECRET_KEY=change-me-to-a-long-random-string
```

### 5. (Optional) Generate demo PDFs

```bash
python create_sample_pdfs.py
```

This creates 3 synthetic discharge summaries in `pdf_samples/`:
- `demo_case_01_simple.pdf` — simple discharge, few medications
- `demo_case_02_polypharmacy.pdf` — elderly polypharmacy with medication changes
- `demo_case_03_followups.pdf` — multiple follow-ups with calculated due dates

---

## Running the App

### Web application

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) and log in with `demo / demo123` (or whatever you set in `.env`).

**Demo flow:**
1. Log in
2. Upload a PDF from `pdf_samples/`
3. Wait 10–20 seconds for LLM extraction
4. View the structured Clinical Snapshot

### CLI (pipeline only)

```bash
python run_pipeline.py "pdf_samples/demo_case_02_polypharmacy.pdf"
```

Options:

| Flag | Description |
|---|---|
| `--save` | Save result to SQLite (`data/snapshots.db`) |
| `--db path/to.db` | Custom database path |
| `--json` | Print output as JSON instead of table |

---

## Data Model

```python
ClinicalSummary
├── patient_name: str
├── age: int
├── discharge_date: str
├── conditions: List[Condition]       # name, status, notes
├── medications: List[Medication]     # name, dose, frequency, status
├── follow_ups: List[FollowUp]        # specialty, timeframe, due_date
└── recent_events: List[Event]        # type, date, reason
```

---

## Limitations

- **Text-based PDFs only** — scanned/image PDFs are not supported (OCR is a planned enhancement)
- **LLM accuracy** — extraction quality depends on document structure and LLM response; always verify outputs
- **Single demo user** — authentication is minimal by design for the hackathon scope
- **No real EMR integration** — uses synthetic/de-identified sample documents

---

## Roadmap

- [ ] OCR support for scanned PDFs
- [ ] Polypharmacy rule engine (flag >5 medications)
- [ ] Multi-document patient timeline merging
- [ ] Downloadable JSON export
- [ ] EMR integration layer
- [ ] Role-based access (clinician vs caretaker view)

---

## License

This project was built for a hackathon demonstration. Not intended for clinical use.
