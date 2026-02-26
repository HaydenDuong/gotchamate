"""LLM-based extraction of structured JSON from discharge summary text."""

import json
import os
import re
from pipeline.models import ClinicalSummary

# JSON schema matching our Pydantic models for the prompt
EXTRACTION_SCHEMA = """
{
  "patient_name": "string",
  "age": integer (0-150),
  "discharge_date": "string (e.g. 2024-06-05, or N/A if not found)",
  "conditions": [
    {"name": "string", "status": "string (active or historical)", "notes": "string or empty"}
  ],
  "medications": [
    {
      "name": "string",
      "dose": "string or N/A",
      "frequency": "string or N/A",
      "status": "string — one of: New, Stopped, Dose Changed, Continuing, N/A. Use keywords: commenced/started=New, ceased/stopped/discontinued=Stopped, increased/reduced/changed=Dose Changed, continuing/unchanged=Continuing, otherwise N/A"
    }
  ],
  "follow_ups": [
    {
      "specialty": "string (e.g. GP, Cardiology)",
      "recommended_timeframe": "string (e.g. in 2 weeks) or N/A",
      "due_date": "string — if discharge_date is known and timeframe is given, calculate the estimated due date (YYYY-MM-DD). Otherwise N/A"
    }
  ],
  "recent_events": [
    {"type": "string (e.g. admission, discharge)", "date": "string or N/A", "reason": "string or empty"}
  ]
}
"""

SYSTEM_PROMPT = """You are a clinical document extraction engine.
Extract structured data from the following discharge summary or clinical document.
Return ONLY valid JSON matching this schema exactly. Do not include markdown, code fences, or any explanation.

Rules:
- Use "N/A" (not null, not empty string) when a value is not present or cannot be determined.
- For medication status, classify using these keywords if present:
    commenced / started → New
    ceased / stopped / discontinued → Stopped
    increased / reduced / dose changed → Dose Changed
    continuing / unchanged / no change → Continuing
    if no keyword found → N/A
- For follow_up due_date: if both discharge_date and a timeframe are available, calculate the estimated date (YYYY-MM-DD). Otherwise use N/A.

Schema:
""" + EXTRACTION_SCHEMA.strip()


def _strip_json_raw(raw: str) -> str:
    """Remove markdown code fences and surrounding text to get raw JSON."""
    raw = raw.strip()
    # Remove ```json ... ``` or ``` ... ```
    for pattern in (r"```(?:json)?\s*([\s\S]*?)\s*```", r"^([\s\S]*?)$"):
        m = re.search(pattern, raw, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return raw


def _call_openai(text: str, model: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.1,
    )
    return (resp.choices[0].message.content or "").strip()


def _call_gemini(text: str, model: str) -> str:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    resp = client.models.generate_content(
        model=model,
        contents=f"{SYSTEM_PROMPT}\n\nDocument text:\n\n{text}",
        config=types.GenerateContentConfig(temperature=0.1),
    )
    if not resp or not getattr(resp, "text", None):
        raise RuntimeError("Gemini returned no text")
    return resp.text.strip()


def extract_clinical_summary(text: str) -> ClinicalSummary:
    """
    Run LLM extraction on raw document text and return a validated ClinicalSummary.

    Uses GEMINI_API_KEY if set, otherwise OPENAI_API_KEY. At least one must be set.

    Raises:
        ValueError: If no API key is set or JSON parsing/validation fails.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if gemini_key:
        # Use a valid model id, e.g. gemini-2.5-flash, gemini-3.1-pro-preview
        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        raw = _call_gemini(text, model)
    elif openai_key:
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        raw = _call_openai(text, model)
    else:
        raise ValueError(
            "Set either GEMINI_API_KEY or OPENAI_API_KEY in your environment (.env)."
        )

    json_str = _strip_json_raw(raw)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}") from e

    return ClinicalSummary.model_validate(data)
