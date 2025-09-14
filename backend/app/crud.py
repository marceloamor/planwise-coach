from sqlalchemy.orm import Session
from sqlalchemy import desc
from .models import Plan, Conversation
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

def save_message(db: Session, client_id: str, role: str, content: str):
    """Save a conversation message to the database."""
    message = Conversation(client_id=client_id, role=role, content=content)
    db.add(message)
    db.commit()

def get_recent_messages(db: Session, client_id: str, limit: int = 15) -> List[Conversation]:
    """Get recent conversation messages for context, excluding system messages."""
    return db.query(Conversation)\
        .filter(Conversation.client_id == client_id)\
        .filter(Conversation.role != "system")\
        .order_by(desc(Conversation.created_at))\
        .limit(limit)\
        .all()

def get_current_plan(db: Session, client_id: str) -> Optional[Plan]:
    """Get the current active plan for a client."""
    return db.query(Plan)\
        .filter(Plan.client_id == client_id)\
        .filter(Plan.is_current == True)\
        .first()

def create_new_plan(db: Session, client_id: str, plan_json: dict) -> Plan:
    """Create a new plan version, marking previous ones as non-current."""
    # Mark existing plans as non-current
    db.query(Plan)\
        .filter(Plan.client_id == client_id)\
        .update({"is_current": False})
    
    # Get next version number
    latest = db.query(Plan)\
        .filter(Plan.client_id == client_id)\
        .order_by(desc(Plan.version))\
        .first()
    
    next_version = (latest.version + 1) if latest else 1
    
    # Create new plan
    new_plan = Plan(
        client_id=client_id,
        version=next_version,
        plan_json=plan_json,
        is_current=True,
        created_at=datetime.utcnow()
    )
    
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    
    logger.info(f"Created plan version {next_version} for client {client_id}")
    return new_plan

def get_plan_history(db: Session, client_id: str, limit: int = 10) -> List[Plan]:
    """Get plan history for a client, most recent first."""
    return db.query(Plan)\
        .filter(Plan.client_id == client_id)\
        .order_by(desc(Plan.created_at))\
        .limit(limit)\
        .all() 