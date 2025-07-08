from sqlalchemy.orm import Session
from app.core.models import Conversation, Message, User
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException
from uuid import UUID
from app.utils.logging_utils import get_secure_logger

logger = get_secure_logger(__name__)

async def get_conversation_messages(
    conversation_id: UUID,
    user_id: UUID,
    db: Session
) -> List[Dict[str, Any]]:
    """Get all messages for a specific conversation."""
    logger.debug("Fetching conversation messages", conversation_id=conversation_id, user_id=user_id)
    
    try:
        messages = db.query(Message)\
            .filter(
                Message.conversation_id == conversation_id
            )\
            .order_by(Message.created_at.asc())\
            .all()
        
        logger.debug("Messages retrieved", conversation_id=conversation_id, count=len(messages))
        
        return [
            {
                "id": str(message.id),
                "content": message.content,
                "role": message.role,
                "created_at": message.created_at.isoformat() + "Z"
            } for message in messages
        ]
        
    except Exception as e:
        logger.error("Error fetching conversation messages", conversation_id=conversation_id, user_id=user_id, error=str(e))
        raise

async def send_message_to_conversation(
    conversation_id: UUID,
    role: str,
    content: str,
    db: Session
) -> Dict[str, Any]:
    """Send a message to a specific conversation."""
    logger.debug("Sending message to conversation", conversation_id=conversation_id, role=role, content=content)

    try:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.now(timezone.utc)
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        logger.info("Message sent successfully", message_id=message.id, conversation_id=conversation_id, role=role)
        
        return {
            "id": str(message.id),
            "conversation_id": str(conversation_id),
            "content": message.content,
            "role": message.role,
            "created_at": message.created_at.isoformat() + "Z"
        }
    except Exception as e:
        logger.error("Error sending message", conversation_id=conversation_id, role=role, error=str(e))
        raise

async def process_previous_messages(conversation_id: UUID, user_id: UUID, db: Session, k_messages: int = 5) -> List[Dict[str, Any]]:
    """Process previous messages in a conversation."""
    logger.debug("Processing previous messages", conversation_id=conversation_id, user_id=user_id, k_messages=k_messages)
    
    try:
        messages = await get_conversation_messages(conversation_id, user_id, db)
        processed_messages = messages[-k_messages:]
        
        logger.debug("Previous messages processed", conversation_id=conversation_id, processed_count=len(processed_messages))
        return processed_messages
    except Exception as e:
        logger.error("Error processing previous messages", conversation_id=conversation_id, user_id=user_id, error=str(e))
        raise

