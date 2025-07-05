from sqlalchemy.orm import Session
from app.core.models import Conversation, Message, User
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timezone
from fastapi import HTTPException
from uuid import UUID

logger = logging.getLogger(__name__)

async def get_user_conversations(
    user_id: UUID, 
    db: Session,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0
) -> List[Dict[str, Any]]:
    """
    Get all conversations for a specific user.
    Returns a list of conversation dictionaries in JSON format.
    """
    try:
        logger.info(f"Getting conversations for user {user_id} with limit {limit} and offset {offset}")
        conversations = db.query(Conversation)\
            .filter(Conversation.user_id == user_id)\
            .order_by(Conversation.updated_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        logger.debug(f"Found {len(conversations)} conversations for user {user_id}")
        # Convert SQLAlchemy objects to dictionaries
        conversations_json = []
        for conv in conversations:
            conversations_json.append({
                "id": str(conv.id),
                "title": conv.title,
                "summary": conv.summary,
                "created_at": conv.created_at.isoformat() + "Z",
                "updated_at": conv.updated_at.isoformat() + "Z"
            })
        
        logger.info(f"Retrieved {len(conversations_json)} conversations for user {user_id}")
        return conversations_json
        
    except Exception as e:
        logger.error(f"Error getting conversations for user {user_id}: {str(e)}")
        raise

async def get_conversation_by_id(
    conversation_id: UUID,
    user_id: UUID,
    db: Session
) -> Conversation:
    """Get a specific conversation by ID for a user."""
    try:
        conversation = db.query(Conversation)\
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )\
            .first()
        
        if not conversation:
            return None
            
        return conversation
        
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {str(e)}")
        raise

async def create_conversation(
    user_id: UUID,
    title: str,
    db: Session
) -> Dict[str, Any]:
    """Create a new conversation for a user."""
    logger.info(f"Creating conversation for user {user_id} with title '{title}'")
    try:
        conversation = Conversation(
            user_id=user_id,
            title=title,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        logger.debug(f"New conversation object created: {conversation}")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Created conversation {conversation.id} for user {user_id}")
        
        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat() + "Z",
            "updated_at": conversation.updated_at.isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        db.rollback()
        raise

async def update_conversation_summary(
    conversation_id: UUID,
    user_id: UUID,
    summary: str,
    db: Session
) -> Dict[str, Any]:
    """Update the summary of a conversation."""
    try:
        conversation = db.query(Conversation)\
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )\
            .first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation.summary = summary
        conversation.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Updated summary for conversation {conversation_id}")
        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "summary": conversation.summary,
            "updated_at": conversation.updated_at.isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error updating conversation summary: {str(e)}")
        raise