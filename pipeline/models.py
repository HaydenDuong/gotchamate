"""Pydantic models for the clinical snapshot schema."""

from pydantic import BaseModel, Field


class Condition(BaseModel):
    name: str = Field(description="Condition or diagnosis name")
    status: str = Field(description="e.g. active, historical")
    notes: str = Field(default="", description="Optional notes")


class Medication(BaseModel):
    name: str = Field(description="Medication name")
    dose: str = Field(default="", description="Dose e.g. 10mg")
    frequency: str = Field(default="", description="Frequency e.g. twice daily")


class FollowUp(BaseModel):
    specialty: str = Field(description="e.g. Cardiology, GP")
    recommended_timeframe: str = Field(default="", description="e.g. in 2 weeks")


class Event(BaseModel):
    type: str = Field(description="e.g. admission, discharge")
    date: str = Field(default="", description="Date of event")
    reason: str = Field(default="", description="Reason or summary")


class ClinicalSummary(BaseModel):
    patient_name: str = Field(description="Patient name from document")
    age: int = Field(description="Patient age", ge=0, le=150)
    conditions: list[Condition] = Field(default_factory=list)
    medications: list[Medication] = Field(default_factory=list)
    follow_ups: list[FollowUp] = Field(default_factory=list)
    recent_events: list[Event] = Field(default_factory=list)
