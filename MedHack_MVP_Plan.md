# MedHack MVP Execution Plan

## Project Focus

Build a **Discharge Intelligence Engine** that: - Extracts medications
from discharge summaries - Extracts follow-up instructions - Structures
the information clearly - Displays it in a clinician-friendly and
caretaker-friendly format

The system does NOT: - Provide medical advice - Recommend treatment
changes - Predict risk - Perform clinical decision-making

------------------------------------------------------------------------

# 1. Core Architecture

## Pipeline Overview

Upload PDF\
→ Preprocessing (text extraction)\
→ LLM Structured Extraction\
→ Validation Layer\
→ Structured JSON\
→ Web Dashboard Rendering

------------------------------------------------------------------------

# 2. Must-Have Components

## A. Structured Extraction

Extract:

-   Patient Information
-   Current Medications
-   Medication Changes (New / Stopped / Dose Changed)
-   Follow-up Instructions
-   Discharge Date

------------------------------------------------------------------------

## B. Validation Layer (Critical)

Implement:

-   Strict schema (DTO / Pydantic model)
-   Required field checks
-   Null handling
-   Confidence flag (optional but recommended)

Example schema:

    {
      "medications": [
        {
          "name": "Ramipril",
          "dose": "10mg",
          "frequency": "daily",
          "status": "Dose Increased",
          "confidence": 0.92
        }
      ],
      "follow_up": [
        {
          "task": "GP Review",
          "timeframe": "5 days"
        }
      ]
    }

------------------------------------------------------------------------

## C. Medication Status Detection

Use simple keyword logic:

-   "commenced", "started" → New
-   "ceased", "stopped" → Discontinued
-   "increased", "reduced" → Dose Changed

Add a `Status` column in table.

------------------------------------------------------------------------

## D. Follow-up Timeline Logic

Parse time expressions:

-   "5 days"
-   "1 week"
-   "2 weeks"

Calculate estimated due date based on discharge date.

Display as:

Next Actions: - Day 5: GP Review - Day 7: Blood Test - Week 2:
Cardiology Clinic

------------------------------------------------------------------------

# 3. UI Requirements

## Patient / Caretaker View

Simple Table:

  Medication   Dose   Frequency   Status
  ------------ ------ ----------- --------

Follow-up section: - Bullet list or timeline

Clear disclaimer: "AI-generated summary. Requires clinician
verification."

------------------------------------------------------------------------

## Clinician View

Additional structured sections:

-   Allergies
-   Chronic Conditions
-   Past Surgeries
-   Current Medications
-   Medication Changes
-   Follow-up Tasks

No free-text blocks.

------------------------------------------------------------------------

# 4. What NOT To Add

Do NOT implement:

-   Drug interaction checker
-   Dosage safety warnings
-   Risk prediction models
-   Complex discrepancy engine
-   Notification reminder system

These dilute focus.

------------------------------------------------------------------------

# 5. Demo Strategy

Prepare 3 cases:

1.  Simple discharge
2.  Polypharmacy elderly case
3.  Case with multiple follow-ups

Demo Flow:

1.  Upload PDF
2.  Show structured dashboard
3.  Highlight medication changes
4.  Show follow-up timeline

------------------------------------------------------------------------

# 6. Pitch Positioning

Problem Statement:

Transition of care after hospital discharge creates cognitive overload
for GPs, caretakers, and elderly patients. Important medication changes
and follow-up tasks are buried in narrative PDFs.

Solution:

We structure discharge summaries into workflow-ready clinical data,
reducing information fragmentation and improving clarity.

Boundary:

This tool assists review. Final decisions remain with clinicians.

------------------------------------------------------------------------

# 7. 48-Hour Execution Plan

Day 1: - Finalize schema - Implement validation - Implement medication
status tagging

Day 2: - Implement follow-up timeline logic - Build clean dashboard UI -
Prepare demo cases

Day 3: - Polish UI - Prepare architecture slide - Rehearse pitch and Q&A

------------------------------------------------------------------------

# End Goal

Deliver a focused, safe, technically credible MVP that demonstrates:

-   Strong backend architecture
-   Healthcare workflow understanding
-   Responsible AI usage
