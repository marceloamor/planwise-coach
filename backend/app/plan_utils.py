"""
Plan utility functions for comparison and analysis.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

def compare_plans(old_plan: Dict[str, Any], new_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two plans and return a summary of changes.
    Returns a dict with change analysis.
    """
    changes = {
        "goal_changed": False,
        "weeks_changed": False,
        "week_count_changed": False,
        "sessions_modified": False,
        "constraints_changed": False,
        "summary": []
    }
    
    if not old_plan or not new_plan:
        changes["summary"].append("Plan created or completely replaced")
        return changes
    
    # Compare meta information
    old_meta = old_plan.get("meta", {})
    new_meta = new_plan.get("meta", {})
    
    if old_meta.get("goal") != new_meta.get("goal"):
        changes["goal_changed"] = True
        changes["summary"].append(f"Goal changed from {old_meta.get('goal')} to {new_meta.get('goal')}")
    
    # Compare week count
    old_weeks = old_plan.get("weeks", {})
    new_weeks = new_plan.get("weeks", {})
    
    if len(old_weeks) != len(new_weeks):
        changes["week_count_changed"] = True
        changes["weeks_changed"] = True
        changes["summary"].append(f"Plan length changed from {len(old_weeks)} to {len(new_weeks)} weeks")
    
    # Compare weekly structure
    for week_key in set(old_weeks.keys()) | set(new_weeks.keys()):
        if week_key not in old_weeks:
            changes["weeks_changed"] = True
            changes["summary"].append(f"Added {week_key}")
        elif week_key not in new_weeks:
            changes["weeks_changed"] = True
            changes["summary"].append(f"Removed {week_key}")
        else:
            # Compare sessions within the week
            old_sessions = old_weeks[week_key].get("sessions", [])
            new_sessions = new_weeks[week_key].get("sessions", [])
            
            if len(old_sessions) != len(new_sessions):
                changes["sessions_modified"] = True
                changes["summary"].append(f"Session count changed in {week_key}")
    
    # Compare constraints
    old_constraints = old_plan.get("constraints", {})
    new_constraints = new_plan.get("constraints", {})
    
    if old_constraints != new_constraints:
        changes["constraints_changed"] = True
        changes["summary"].append("Training constraints modified")
    
    # Overall assessment
    if not any([changes["goal_changed"], changes["weeks_changed"], changes["sessions_modified"], changes["constraints_changed"]]):
        changes["summary"].append("No significant changes detected")
    
    return changes

def extract_plan_summary(plan: Dict[str, Any]) -> str:
    """
    Extract a concise summary of a plan for logging/debugging.
    """
    if not plan:
        return "No plan"
    
    meta = plan.get("meta", {})
    weeks = plan.get("weeks", {})
    
    goal = meta.get("goal", "Unknown")
    week_count = len(weeks)
    phase = meta.get("phase", "Unknown")
    
    # Count total sessions
    total_sessions = sum(len(week.get("sessions", [])) for week in weeks.values())
    
    return f"{goal} plan: {week_count} weeks, {total_sessions} total sessions, {phase} phase"

def validate_plan_modification_request(user_message: str, current_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze user message to determine if it's a modification request and what type.
    """
    message_lower = user_message.lower()
    
    analysis = {
        "is_modification": False,
        "modification_type": None,
        "detected_patterns": []
    }
    
    if not current_plan:
        return analysis
    
    # Detect modification patterns
    modification_patterns = [
        ("extend", ["extend", "make it longer", "add more weeks", "12 weeks", "16 weeks"]),
        ("intensity", ["easier", "harder", "more intense", "less intense", "too hard", "too easy"]),
        ("schedule", ["different days", "move to", "change days", "weekend", "weekday"]),
        ("race_constraint", ["race", "event", "competition", "5k", "10k", "half marathon", "marathon"]),
        ("session_type", ["more", "add", "include", "remove", "less"])
    ]
    
    for mod_type, patterns in modification_patterns:
        for pattern in patterns:
            if pattern in message_lower:
                analysis["is_modification"] = True
                analysis["modification_type"] = mod_type
                analysis["detected_patterns"].append(pattern)
                break
        if analysis["is_modification"]:
            break
    
    return analysis 