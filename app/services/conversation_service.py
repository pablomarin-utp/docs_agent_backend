from sqlalchemy.orm import Session
from app.core.models import Conversation, Message, User
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException
from uuid import UUID
from app.utils.logging_utils import get_secure_logger

logger = get_secure_logger(__name__)

async def get_user_conversations(
    user_id: UUID, 
    db: Session,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0
) -> List[Dict[str, Any]]:
    """
    Get all conversations for a specific user.
    
    Args:
        user_id: UUID of the user
        db: Database session
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip
        
    Returns:
        List of conversation dictionaries in JSON format
    """
    logger.info("Fetching user conversations", user_id=user_id, limit=limit, offset=offset)
    
    try:
        conversations = db.query(Conversation)\
            .filter(Conversation.user_id == user_id)\
            .order_by(Conversation.updated_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        logger.debug("Conversations query completed", user_id=user_id, count=len(conversations))
        
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
        
        logger.info("Conversations retrieved successfully", user_id=user_id, count=len(conversations_json))
        return conversations_json
        
    except Exception as e:
        logger.error("Error fetching user conversations", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")

async def get_conversation_by_id(
    conversation_id: UUID,
    user_id: UUID,
    db: Session
) -> Conversation:
    """
    Get a specific conversation by ID for a user.
    
    Args:
        conversation_id: UUID of the conversation
        user_id: UUID of the user
        db: Database session
        
    Returns:
        Conversation object or None if not found
    """
    logger.debug("Fetching conversation by ID", conversation_id=conversation_id, user_id=user_id)
    
    try:
        conversation = db.query(Conversation)\
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )\
            .first()
        
        if not conversation:
            logger.warning("Conversation not found", conversation_id=conversation_id, user_id=user_id)
            return None
        
        logger.debug("Conversation found", conversation_id=conversation_id, user_id=user_id)
        return conversation
        
    except Exception as e:
        logger.error("Error fetching conversation", conversation_id=conversation_id, user_id=user_id, error=str(e))
        raise

async def create_conversation(
    user_id: UUID,
    title: str,
    db: Session
) -> Dict[str, Any]:
    """
    Create a new conversation for a user.
    
    Args:
        user_id: UUID of the user
        title: Title of the conversation
        db: Database session
        
    Returns:
        Dictionary with conversation data
    """
    logger.info("Creating new conversation", user_id=user_id, title=title)
    
    try:
        conversation = Conversation(
            user_id=user_id,
            title=title,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        logger.info("Conversation created successfully", conversation_id=conversation.id, user_id=user_id)
        
        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat() + "Z",
            "updated_at": conversation.updated_at.isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error("Error creating conversation", user_id=user_id, error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create conversation")

async def update_conversation_summary(
    conversation_id: UUID,
    user_id: UUID,
    summary: str,
    db: Session
) -> Dict[str, Any]:
    """
    Update the summary of a conversation.
    
    Args:
        conversation_id: UUID of the conversation
        user_id: UUID of the user
        summary: New summary text
        db: Database session
        
    Returns:
        Dictionary with updated conversation data
    """
    logger.debug("Updating conversation summary", conversation_id=conversation_id, user_id=user_id)
    
    try:
        conversation = db.query(Conversation)\
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )\
            .first()
        
        if not conversation:
            logger.warning("Conversation not found for summary update", conversation_id=conversation_id, user_id=user_id)
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation.summary = summary
        conversation.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(conversation)
        
        logger.info("Conversation summary updated", conversation_id=conversation_id, user_id=user_id)
        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "summary": conversation.summary,
            "updated_at": conversation.updated_at.isoformat() + "Z"
        }
    except Exception as e:
        logger.error("Error updating conversation summary", conversation_id=conversation_id, user_id=user_id, error=str(e))
        raise

async def delete_conversation_service(
    conversation_id: UUID,
    user_id: UUID,
    db: Session
) -> bool:
    """
    Delete a conversation and all its messages for a user.
    
    Args:
        conversation_id: UUID of the conversation
        user_id: UUID of the user
        db: Database session
        
    Returns:
        True if deletion was successful
        
    Raises:
        HTTPException: If conversation not found or deletion fails
    """
    logger.info("Deleting conversation", conversation_id=conversation_id, user_id=user_id)
    
    try:
        # Find the conversation that belongs to the user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            logger.warning("Conversation not found for deletion", conversation_id=conversation_id, user_id=user_id)
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Delete messages first
        messages_deleted = db.query(Message).filter(Message.conversation_id == conversation_id).delete()
        logger.debug("Messages deleted", conversation_id=conversation_id, count=messages_deleted)
        
        # Delete conversation
        db.delete(conversation)
        db.commit()
        
        logger.info("Conversation deleted successfully", conversation_id=conversation_id, user_id=user_id)
        return True
        
    except Exception as e:
        logger.error("Error deleting conversation", conversation_id=conversation_id, user_id=user_id, error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete conversation")
