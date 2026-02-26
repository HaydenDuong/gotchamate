"""
Generate 3 synthetic text-based discharge summary PDFs for demo use.

    Case 1: Simple discharge (single condition, few medications, one follow-up)
    Case 2: Polypharmacy elderly case (>5 medications with status changes)
    Case 3: Multiple follow-ups with clear dates

Run:
    pip install fpdf2
    python create_sample_pdfs.py
"""

from pathlib import Path
from fpdf import FPDF


def make_pdf(filename: str, title: str, lines: list[str]) -> None:
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    effective_w = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(effective_w, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 11)

    for line in lines:
        if line == "---":
            pdf.ln(3)
            pdf.set_draw_color(180, 180, 180)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(4)
        elif line.startswith("## "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(effective_w, 8, line[3:], new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
        elif line.strip() == "":
            pdf.ln(3)
        else:
            pdf.multi_cell(effective_w, 7, line, new_x="LMARGIN", new_y="NEXT")

    out = Path("pdf_samples") / filename
    out.parent.mkdir(exist_ok=True)
    pdf.output(str(out))
    print(f"Created: {out}")


# Case 1: Simple discharge
make_pdf(
    "demo_case_01_simple.pdf",
    "DISCHARGE SUMMARY - CASE 1",
    [
        "## Patient Information",
        "Name: Margaret Williams",
        "Date of Birth: 12/03/1948    Age: 76",
        "MRN: 100234",
        "Discharge Date: 05/06/2024",
        "---",
        "## Admission Details",
        "Admission Date: 01/06/2024",
        "Reason for Admission: Community-acquired pneumonia",
        "Ward: General Medicine",
        "---",
        "## Active Conditions",
        "1. Community-Acquired Pneumonia (active)",
        "2. Type 2 Diabetes Mellitus (active)",
        "---",
        "## Medications on Discharge",
        "1. Amoxicillin-Clavulanate 875/125mg PO BID x 5 days   [commenced]",
        "2. Metformin 500mg PO BD   [continuing, no change]",
        "3. Paracetamol 1g PO QID PRN",
        "---",
        "## Follow-up Instructions",
        "1. Review with GP in 5 days (10/06/2024) to assess recovery.",
        "2. Repeat chest X-ray in 6 weeks.",
        "---",
        "## Discharge Notes",
        "Patient responded well to IV antibiotics. Switched to oral on Day 2.",
        "Advised to complete the full antibiotic course and maintain hydration.",
        "---",
        "AI-extracted structured summary - requires clinician verification.",
    ],
)

# Case 2: Polypharmacy elderly case
make_pdf(
    "demo_case_02_polypharmacy.pdf",
    "DISCHARGE SUMMARY - CASE 2",
    [
        "## Patient Information",
        "Name: Robert Chen",
        "Date of Birth: 22/11/1942    Age: 81",
        "MRN: 200456",
        "Discharge Date: 08/06/2024",
        "---",
        "## Admission Details",
        "Admission Date: 02/06/2024",
        "Reason for Admission: Decompensated heart failure",
        "Ward: Cardiology",
        "---",
        "## Active Conditions",
        "1. Congestive Heart Failure (active)",
        "2. Atrial Fibrillation (active)",
        "3. Type 2 Diabetes Mellitus (active)",
        "4. Chronic Kidney Disease Stage 3 (active)",
        "5. Hypertension (active)",
        "6. Hypercholesterolaemia (active)",
        "---",
        "## Medications on Discharge",
        "CHANGES MADE DURING ADMISSION:",
        "1. Furosemide 40mg PO daily   [dose increased from 20mg - fluid overload]",
        "2. Spironolactone 25mg PO daily   [commenced - adjunct HF therapy]",
        "3. Digoxin 125mcg PO daily   [commenced - rate control for AF]",
        "4. Metformin 500mg PO BD   [ceased - CKD progression, eGFR <45]",
        "5. Empagliflozin 10mg PO daily   [commenced - replacing Metformin]",
        "",
        "CONTINUING UNCHANGED:",
        "6. Bisoprolol 5mg PO daily   [continuing]",
        "7. Ramipril 5mg PO daily   [continuing]",
        "8. Atorvastatin 40mg PO nocte   [continuing]",
        "9. Apixaban 5mg PO BD   [continuing - AF anticoagulation]",
        "10. Pantoprazole 40mg PO daily   [continuing]",
        "---",
        "## Follow-up Instructions",
        "1. Cardiology clinic in 2 weeks (22/06/2024).",
        "2. GP review in 5 days (13/06/2024) - renal function and electrolytes.",
        "3. Diabetes educator review in 3 weeks (29/06/2024).",
        "---",
        "## Discharge Notes",
        "Patient stabilised after IV diuresis. Weight reduced by 4.2kg.",
        "Family educated on fluid restriction and daily weight monitoring.",
        "---",
        "AI-extracted structured summary - requires clinician verification.",
    ],
)

# Case 3: Multiple follow-ups with dates
make_pdf(
    "demo_case_03_followups.pdf",
    "DISCHARGE SUMMARY - CASE 3",
    [
        "## Patient Information",
        "Name: Dorothy Nguyen",
        "Date of Birth: 07/07/1950    Age: 73",
        "MRN: 300789",
        "Discharge Date: 10/06/2024",
        "---",
        "## Admission Details",
        "Admission Date: 05/06/2024",
        "Reason for Admission: Elective right total knee replacement",
        "Ward: Orthopaedics",
        "---",
        "## Active Conditions",
        "1. Right Knee Osteoarthritis (active - post-operative)",
        "2. Hypertension (active)",
        "3. Osteoporosis (active)",
        "---",
        "## Medications on Discharge",
        "1. Oxycodone 5mg PO QID PRN x 7 days   [commenced - post-op analgesia]",
        "2. Celecoxib 200mg PO BD x 2 weeks   [commenced - anti-inflammatory]",
        "3. Enoxaparin 40mg SC daily x 4 weeks   [commenced - DVT prophylaxis]",
        "4. Amlodipine 5mg PO daily   [continuing]",
        "5. Alendronate 70mg PO weekly   [continuing]",
        "6. Calcium + Vitamin D 600/400 PO daily   [continuing]",
        "---",
        "## Follow-up Instructions",
        "1. Wound review with GP in 3 days (13/06/2024).",
        "2. Physiotherapy - outpatient, commencing 14/06/2024, twice weekly x 6 weeks.",
        "3. Orthopaedic surgeon review in 6 weeks (22/07/2024) - post-op X-ray.",
        "4. Bone density scan (DEXA) in 6 months.",
        "5. Anaemia check (FBC) with GP in 2 weeks (24/06/2024).",
        "---",
        "## Discharge Notes",
        "Uncomplicated surgical recovery. Mobilising with frame, physio commenced.",
        "Patient and daughter educated on DVT prevention and wound care.",
        "---",
        "AI-extracted structured summary - requires clinician verification.",
    ],
)

print("\nAll 3 demo PDFs created in pdf_samples/")
