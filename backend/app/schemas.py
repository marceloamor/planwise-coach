from typing import List, Literal, Optional, Union, Dict
from pydantic import BaseModel, Field, field_validator
from datetime import date

Intensity = Literal["E","M","T","I","R","H","S","X"]  # Easy, Marathon, Threshold, Intervals, Reps, Hills, Strides, Cross

class Session(BaseModel):
    date: Optional[date] = None
    type: str = Field(min_length=1)  # At least non-empty
    distance_km: Optional[float] = None
    time_min: Optional[int] = None
    intensity: Optional[Intensity] = None
    rpe: Optional[int] = Field(default=None, ge=1, le=10)
    structure: Optional[str] = None
    notes: Optional[str] = None
    day_of_week: Optional[Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]] = None
    is_rest_day: Optional[bool] = False

    @field_validator("distance_km")
    @classmethod
    def reasonable_distance(cls, v):
        if v is not None and (v < 0 or v > 100):  # Very loose bounds for MVP
            raise ValueError("Distance seems unrealistic (0-100km)")
        return v
        
    @field_validator("time_min")
    @classmethod
    def reasonable_time(cls, v):
        if v is not None and (v < 0 or v > 600):  # 0-10 hours seems reasonable
            raise ValueError("Time seems unrealistic (0-600min)")
        return v

class WeekPlan(BaseModel):
    mileage_target: Optional[float] = None
    sessions: List[Session] = Field(min_length=1)  # At least one session per week

class PlanMeta(BaseModel):
    goal: str = Field(description="Training goal like '5K', 'Half Marathon', etc.")
    race_date: Optional[date] = None
    phase: str = Field(default="Base", description="Training phase")
    weekly_km_target: Optional[float] = Field(default=None, ge=1, le=200)

class PlanConstraints(BaseModel):
    max_weekly_increase_pct: int = Field(default=15, ge=5, le=50)
    min_rest_days: int = Field(default=1, ge=0, le=3)

class PlanDoc(BaseModel):
    meta: PlanMeta = Field(description="Plan metadata including goal and phase")
    constraints: PlanConstraints = Field(default_factory=lambda: PlanConstraints())
    weeks: Dict[str, WeekPlan] = Field(description="Weekly training structure", min_length=1)
    
    @field_validator("weeks")
    @classmethod
    def validate_weeks_structure(cls, v):
        if not v:
            raise ValueError("Plan must include at least one week")
        
        # Ensure week keys are properly formatted
        for week_key in v.keys():
            if not week_key.startswith("week_"):
                raise ValueError(f"Week key must start with 'week_': {week_key}")
        
        return v

    @field_validator("weeks")
    @classmethod
    def must_have_sessions(cls, v):
        if not v:
            raise ValueError("Plan must include at least one week.")
        return v

class ChatMessageIn(BaseModel):
    client_id: str
    message: str = Field(min_length=1)

class ChatResponse(BaseModel):
    reply: str
    plan_updated: bool
    plan: Optional[PlanDoc] = None

class PlanResponse(BaseModel):
    plan: Optional[PlanDoc] = None
    version: Optional[int] = None
    created_at: Optional[str] = None 