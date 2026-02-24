Clinical Document Structuring Engine – MVP Plan
1. Project Overview
Problem
Clinical information for elderly patients is often stored in fragmented, unstructured documents such as discharge summaries and specialist letters (PDFs).
Providers must manually review lengthy documents to extract key data including medications, diagnoses, and follow-up instructions.
This process is time-consuming, cognitively demanding, and error-prone.

Solution
Build a backend data pipeline that:
    Accepts uploaded EMR/discharge summary PDFs
    Extracts raw text
    Uses an LLM to convert unstructured text into structured JSON
    Maps the JSON into predefined OOP models
    Displays a clean, structured “Clinical Snapshot” table
The MVP demonstrates how fragmented clinical documents can be transformed into structured, actionable data within seconds.

2. MVP Scope (Strictly Defined)
Included
Upload text-based discharge summary PDFs
Extract:
    Patient name
    Age
    Active conditions
    Medication list
    Recommended follow-ups
    Recent admission event
    Convert into structured JSON
    Map into Python OOP models
    Display structured output in table format

Excluded (Out of Scope)
    Real EMR integration
    National health record integration
    Authentication system
    Chatbot interface
    Advanced clinical decision support
    Real-time synchronization
    Production-grade security implementation

This MVP focuses strictly on structured document extraction.

3. System Architecture
High-Level Flow
PDF Upload
    ↓
Text Extraction (pdfplumber)
    ↓
LLM Extraction (Structured JSON)
    ↓
JSON Validation (Pydantic)
    ↓
Map to OOP Classes
    ↓
Store in SQLite
    ↓
Display Clinical Snapshot Table

4. Tech Stack
Backend
    Python
    FastAPI
    pdfplumber (PDF text extraction)
    OpenAI API (e.g., gpt-4o-mini) OR local LLM via Ollama
    Pydantic (schema validation)
    SQLite (lightweight storage)

Frontend
Option A (recommended for hackathon speed):
    FastAPI templates + HTML table

Option B:
    Simple React frontend consuming backend API

5. Data Model (OOP Design)

ClinicalSummary
    patient_name: str
    age: int
    conditions: List[Condition]
    medications: List[Medication]
    follow_ups: List[FollowUp]
    recent_events: List[Event]

Condition
    name: str
    status: str (active / historical)
    notes: str

Medication
    name: str
    dose: str
    frequency: str

FollowUp
    specialty: str
    recommended_timeframe: str

Event
    type: str (e.g., admission)
    date: str
    reason: str

6. LLM Extraction Strategy

The LLM must:
    Return ONLY valid JSON
    Follow a strict predefined schema
    Avoid narrative or explanation

Example system instruction:
    You are a clinical document extraction engine.
    Extract structured data from the following discharge summary.
    Return ONLY valid JSON following the provided schema.
    Do not include explanations, markdown, or extra text.

Output will be validated using Pydantic before mapping into OOP objects.

7. Demo Scenario
Demo Flow
    Upload discharge summary PDF.
    Show raw extracted text (optional).
    Trigger AI extraction.
    Display structured Clinical Snapshot:
    Active conditions
    Current medications
    Recommended follow-up
    Display medication count and condition count.

Value Proposition
    “We convert fragmented clinical documents into structured, actionable patient state models in seconds.”

8. Risk Mitigation (No Clinician in Team)
Because the team does not include a clinician:
    We will not perform diagnosis inference.
    We will not provide treatment recommendations.
    We will not implement decision support logic.
    All outputs will be labeled:
        “AI-extracted structured summary – requires clinician verification.”

This ensures the MVP remains a technical demonstration rather than a clinical tool.

9. Stretch Goals (If Time Permits)

Flag patients with >5 medications

Merge multiple documents into one patient timeline

Add simple confidence score for extracted fields

Add downloadable JSON export

10. Success Criteria

The MVP is successful if:
    A discharge summary PDF can be uploaded
    The system reliably extracts structured JSON
    JSON passes validation
    Data is mapped to OOP models
    A clean clinical snapshot table is displayed
    The demo runs consistently without crashing

11. Post-Hackathon Vision
Future development may include:
    Rule engine for polypharmacy detection
    Care coordination logic
    Multi-provider data merging
    EMR integration layer
    AI-assisted query interface