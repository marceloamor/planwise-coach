from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from .db import engine, Base
from .schemas import ChatMessageIn, ChatResponse, PlanDoc, PlanResponse
from .crud import save_message, get_current_plan, create_new_plan, get_recent_messages
from .deps import get_db, parse_plan_safely
from .llm import chat_to_plan
from .prompts import SYSTEM_PROMPT
from .plan_utils import compare_plans, extract_plan_summary, validate_plan_modification_request
from .models import Conversation, Plan

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Run Coach - MVP", version="1.0.0")

# CORS for local development (Next.js on 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/plan", response_model=PlanResponse)
def get_plan_endpoint(client_id: str):
    """Get the current plan for a client."""
    with get_db() as db:
        plan = get_current_plan(db, client_id)
        if not plan:
            return PlanResponse(plan=None)
        
        try:
            plan_doc = PlanDoc.model_validate(plan.plan_json)
            return PlanResponse(
                plan=plan_doc,
                version=plan.version,
                created_at=plan.created_at.isoformat()
            )
        except Exception as e:
            logger.error(f"Error validating stored plan: {e}")
            return PlanResponse(plan=None)

@app.delete("/session/{client_id}")
def reset_session(client_id: str):
    """
    Reset/clear all data for a client session.
    Deletes all conversations and plans for the given client_id.
    """
    with get_db() as db:
        try:
            # Delete all conversations for this client
            conversations_deleted = db.query(Conversation)\
                .filter(Conversation.client_id == client_id)\
                .delete()
            
            # Delete all plans for this client
            plans_deleted = db.query(Plan)\
                .filter(Plan.client_id == client_id)\
                .delete()
            
            db.commit()
            
            logger.info(f"Reset session for client {client_id}: {conversations_deleted} conversations, {plans_deleted} plans deleted")
            
            return {
                "success": True,
                "message": f"Session reset successfully",
                "conversations_deleted": conversations_deleted,
                "plans_deleted": plans_deleted
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error resetting session for client {client_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to reset session: {str(e)}"
            )

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    message: ChatMessageIn, 
    x_client_id: str | None = Header(default=None),
    stream: bool = False
):
    """
    Chat endpoint that processes user messages and returns responses with optional plan updates.
    """
    client_id = message.client_id or x_client_id
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id required")

    with get_db() as db:
        # Save user message
        save_message(db, client_id, "user", message.message)

        # Get current plan for context
        current_plan = get_current_plan(db, client_id)
        
        # Build conversation context with plan awareness
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add current plan context if it exists
        if current_plan:
            plan_context = f"""
CURRENT PLAN CONTEXT:
The user already has an active training plan. Here is their current plan structure:

Goal: {current_plan.plan_json.get('meta', {}).get('goal', 'Unknown')}
Phase: {current_plan.plan_json.get('meta', {}).get('phase', 'Unknown')}
Weeks: {len(current_plan.plan_json.get('weeks', {}))} weeks planned
Current Version: {current_plan.version}

When the user asks for modifications, update/extend this existing plan rather than creating a completely new one.
If they ask for extensions (e.g., "make it 12 weeks"), extend the existing plan structure.
If they mention constraints like races, incorporate them into the existing timeline.
"""
            messages.append({"role": "system", "content": plan_context})
            logger.info(f"Added plan context for client {client_id}: {current_plan.plan_json.get('meta', {}).get('goal')} ({len(current_plan.plan_json.get('weeks', {}))} weeks)")
        
        # Load recent conversation for continuity but exclude plan JSON to avoid confusion
        recent = get_recent_messages(db, client_id, limit=10)  # Reduced to 10 since we have plan context
        
        clean_recent = []
        for msg in reversed(recent):  # Reverse to get chronological order
            content = msg.content
            
            # Skip error messages, incomplete responses, and previous plan JSON blocks
            if ("error" in content.lower() or 
                "sorry" in content.lower() or 
                (msg.role == "assistant" and len(content) < 50) or  # Only skip SHORT assistant responses, not user messages
                (msg.role == "assistant" and "PLAN" in content.upper())):  # Skip ALL previous plan JSON
                continue
                
            clean_recent.append({"role": msg.role, "content": content})
        
        messages.extend(clean_recent)
        
        # ALWAYS add the current user message (it's the most important!)
        messages.append({"role": "user", "content": message.message})
        
        logger.info(f"Processing request for client {client_id}: {len(messages)} context messages ({len(clean_recent)} from history, plan_context={current_plan is not None})")

        try:
            # TODO: Add streaming support here later
            # if stream:
            #     from .streaming import create_streaming_response
            #     return create_streaming_response(messages)
            
            # Get LLM response
            raw_response = chat_to_plan(messages)
            
            # Save assistant response
            save_message(db, client_id, "assistant", raw_response)
            
            # Parse response for plan and explanation
            explanation, plan_json = parse_plan_safely(raw_response)
            
            plan_updated = False
            plan_doc = None
            
            # Try to create/update plan if we found valid JSON
            if plan_json:
                try:
                    # Validate against our schema
                    plan_doc = PlanDoc.model_validate(plan_json)
                    
                    # Analyze if this is actually a change from current plan
                    old_plan_data = current_plan.plan_json if current_plan else None
                    new_plan_data = plan_doc.model_dump(mode='json')
                    
                    if old_plan_data:
                        changes = compare_plans(old_plan_data, new_plan_data)
                        logger.info(f"Plan changes detected: {changes['summary']}")
                        
                        # Only create new version if there are meaningful changes
                        if any([changes["goal_changed"], changes["week_count_changed"], changes["sessions_modified"]]):
                            create_new_plan(db, client_id, new_plan_data)
                            plan_updated = True
                            logger.info(f"Plan updated for client {client_id}: {extract_plan_summary(new_plan_data)}")
                        else:
                            logger.info("No significant plan changes detected, keeping current version")
                            plan_updated = False
                    else:
                        # First plan creation
                        create_new_plan(db, client_id, new_plan_data)
                        plan_updated = True
                        logger.info(f"New plan created for client {client_id}: {extract_plan_summary(new_plan_data)}")
                    
                except Exception as e:
                    logger.warning(f"Plan validation/storage failed: {e}")
                    logger.warning(f"Raw plan JSON keys: {list(plan_json.keys()) if plan_json else 'None'}")
                    
                    # Try to return the plan even if storage failed
                    try:
                        plan_doc = PlanDoc.model_validate(plan_json)
                        logger.info("Plan validation succeeded despite storage failure")
                    except Exception as validation_error:
                        logger.error(f"Plan validation also failed: {validation_error}")
                        plan_doc = None
                    
                    # Continue without plan update but potentially with plan display
            
            # Always return the plan to the frontend, even if storage failed
            response_plan = plan_doc if plan_doc else None
            
            return ChatResponse(
                reply=explanation or raw_response,
                plan_updated=plan_updated,
                plan=response_plan
            )
            
        except Exception as e:
            logger.error(f"Chat processing error: {e}")
            # Save error for debugging but return graceful response
            save_message(db, client_id, "assistant", "Sorry, I encountered an error. Please try again.")
            raise HTTPException(
                status_code=500, 
                detail="Sorry, I encountered an error processing your request. Please try again."
            )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 