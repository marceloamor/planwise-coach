from contextlib import contextmanager
from sqlalchemy.orm import Session
from .db import SessionLocal
import json
import re
import logging

logger = logging.getLogger(__name__)

@contextmanager
def get_db():
    """Database dependency for FastAPI."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def extract_json_block(text: str) -> str | None:
    """
    Extract the complete JSON object from text with robust parsing.
    """
    # First try to find content after PLAN marker
    if "PLAN" in text.upper():
        plan_split = text.upper().split("PLAN", 1)
        if len(plan_split) > 1:
            candidate = text.split("PLAN", 1)[1].strip()
            # Remove markdown code block markers if present
            if candidate.startswith("```json"):
                candidate = candidate[7:]
            if candidate.startswith("```"):
                candidate = candidate[3:]
            if candidate.endswith("```"):
                candidate = candidate[:-3]
            candidate = candidate.strip()
        else:
            candidate = text
    else:
        candidate = text
    
    # Find the JSON object - look for balanced braces
    start_idx = candidate.find('{')
    if start_idx == -1:
        return None
        
    brace_count = 0
    end_idx = start_idx
    
    for i, char in enumerate(candidate[start_idx:], start_idx):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i
                break
    
    if brace_count == 0:
        json_str = candidate[start_idx:end_idx + 1]
        # Basic validation that this looks like our expected structure
        if '"meta"' in json_str and '"weeks"' in json_str:
            return json_str
    
    return None

def parse_plan_safely(raw_text: str) -> tuple[str, dict | None]:
    """
    Extract explanation and plan JSON from LLM response with graceful fallbacks.
    Returns (explanation_text, plan_json_dict_or_none)
    """
    # Log the raw response for debugging
    logger.info(f"Parsing response ({len(raw_text)} chars): {raw_text[:200]}...")
    
    # Split on PLAN marker if present
    if "PLAN" in raw_text.upper():
        parts = raw_text.split("PLAN", 1)
        explanation = parts[0].strip()
        json_candidate = parts[1] if len(parts) > 1 else ""
    else:
        explanation = raw_text.strip()
        json_candidate = raw_text
    
    # Try to extract and parse JSON
    json_str = extract_json_block(json_candidate)
    if json_str:
        try:
            plan_json = json.loads(json_str)
            logger.info(f"Successfully parsed JSON with keys: {list(plan_json.keys())}")
            
            # Validate we have the essential structure
            required_top_level = ['meta', 'weeks']
            missing_keys = [key for key in required_top_level if key not in plan_json]
            
            if missing_keys:
                logger.warning(f"JSON missing required keys: {missing_keys}")
                
                # Try to fix common schema issues where AI puts meta fields at top level
                if 'goal' in plan_json and 'meta' not in plan_json:
                    logger.info("Fixing schema: moving top-level meta fields into 'meta' object")
                    meta_fields = {}
                    for field in ['goal', 'race_date', 'phase', 'weekly_km_target']:
                        if field in plan_json:
                            meta_fields[field] = plan_json.pop(field)
                    
                    if meta_fields:
                        plan_json['meta'] = meta_fields
                        logger.info(f"Fixed meta schema")
                
                # Check if we still have critical missing keys
                still_missing = [key for key in required_top_level if key not in plan_json]
                if still_missing:
                    logger.error(f"Cannot fix missing keys: {still_missing}")
                    logger.error(f"Available keys: {list(plan_json.keys())}")
                    return explanation, None
            
            # Validate weeks structure
            if 'weeks' in plan_json:
                weeks = plan_json['weeks']
                if not isinstance(weeks, dict) or not weeks:
                    logger.error("Weeks is not a proper dictionary or is empty")
                    return explanation, None
                    
                # Check that weeks have the expected structure
                for week_key, week_data in weeks.items():
                    if not isinstance(week_data, dict) or 'sessions' not in week_data:
                        logger.error(f"Week {week_key} missing sessions structure")
                        return explanation, None
            
            logger.info(f"Successfully validated JSON structure with keys: {list(plan_json.keys())}")
            return explanation, plan_json
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error: {e}, raw: {json_str[:200]}...")
    else:
        logger.warning("No JSON block found in response")
    
    return explanation, None 