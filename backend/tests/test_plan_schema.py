import pytest
from datetime import date
from app.schemas import PlanDoc, Session, WeekPlan, PlanMeta, PlanConstraints

def test_session_validation():
    """Test that Session model validates correctly."""
    session = Session(
        type="Easy Run",
        distance_km=8.5,
        intensity="E",
        rpe=6,
        day_of_week="monday"
    )
    assert session.type == "Easy Run"
    assert session.distance_km == 8.5
    assert session.intensity == "E"

def test_session_invalid_rpe():
    """Test that invalid RPE values are rejected."""
    with pytest.raises(ValueError):
        Session(type="Easy", rpe=11)

def test_session_invalid_distance():
    """Test that unrealistic distances are rejected."""
    with pytest.raises(ValueError):
        Session(type="Ultra", distance_km=150)

def test_week_plan_validation():
    """Test that WeekPlan requires at least one session."""
    sessions = [
        Session(type="Easy", distance_km=5, intensity="E"),
        Session(type="Rest", is_rest_day=True)
    ]
    week = WeekPlan(mileage_target=25, sessions=sessions)
    assert len(week.sessions) == 2

def test_week_plan_empty_sessions():
    """Test that WeekPlan rejects empty sessions list."""
    with pytest.raises(ValueError):
        WeekPlan(mileage_target=25, sessions=[])

def test_full_plan_validation():
    """Test complete plan validation."""
    sample_plan = {
        "meta": {
            "goal": "Half Marathon", 
            "race_date": "2024-06-15", 
            "phase": "Base", 
            "weekly_km_target": 45
        },
        "constraints": {
            "max_weekly_increase_pct": 12, 
            "min_rest_days": 1
        },
        "weeks": {
            "week_01": {
                "mileage_target": 40,
                "sessions": [
                    {
                        "type": "Easy Run", 
                        "distance_km": 8, 
                        "intensity": "E",
                        "day_of_week": "monday"
                    },
                    {
                        "type": "Threshold Run", 
                        "structure": "3x10min @ T w/2min jog recovery", 
                        "intensity": "T",
                        "day_of_week": "wednesday"
                    },
                    {
                        "type": "Long Run", 
                        "distance_km": 16, 
                        "intensity": "E",
                        "day_of_week": "saturday"
                    },
                    {
                        "type": "Rest",
                        "is_rest_day": True,
                        "day_of_week": "sunday"
                    }
                ]
            },
            "week_02": {
                "mileage_target": 42,
                "sessions": [
                    {
                        "type": "Easy Run", 
                        "distance_km": 8, 
                        "intensity": "E"
                    },
                    {
                        "type": "Intervals", 
                        "structure": "6x800m @ I w/400m jog", 
                        "intensity": "I"
                    },
                    {
                        "type": "Long Run", 
                        "distance_km": 17, 
                        "intensity": "E"
                    }
                ]
            }
        }
    }
    
    plan = PlanDoc.model_validate(sample_plan)
    assert plan.meta.goal == "Half Marathon"
    assert "week_01" in plan.weeks
    assert "week_02" in plan.weeks
    assert len(plan.weeks["week_01"].sessions) == 4
    assert plan.constraints.max_weekly_increase_pct == 12

def test_minimal_plan():
    """Test that a minimal plan still validates."""
    minimal_plan = {
        "meta": {},
        "weeks": {
            "week_01": {
                "sessions": [
                    {"type": "Easy Run"}
                ]
            }
        }
    }
    
    plan = PlanDoc.model_validate(minimal_plan)
    assert plan.meta.goal is None  # Optional field
    assert len(plan.weeks) == 1 