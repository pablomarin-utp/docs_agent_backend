from sqlalchemy.orm import Session
from app.core.models import Conversation, Message, User
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timezone
from fastapi import HTTPException
from uuid import UUID

logger = logging.getLogger(__name__)

async def get_conversation_messages(
    conversation_id: UUID,
    user_id: UUID,
    db: Session
) -> List[Dict[str, Any]]:
    """Get all messages for a specific conversation."""
    try:
        
        messages = db.query(Message)\
            .filter(
                Message.conversation_id == conversation_id
            )\
            .order_by(Message.created_at.asc())\
            .all()
        
        return [
            {
                "id": str(message.id),
                "content": message.content,
                "role": message.role,
                "created_at": message.created_at.isoformat() + "Z"
            } for message in messages
        ]
        
    except Exception as e:
        logger.error(f"Error getting messages for conversation {conversation_id}: {str(e)}")
        raise

async def send_message_to_conversation(
    conversation_id: UUID,
    role: str,
    content: str,
    db: Session
) -> Dict[str, Any]:
    """Send a message to a specific conversation."""

    logger.info(f"Sending message to conversation {conversation_id} for role {role} ")

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

        return {
            "id": str(message.id),
            "conversation_id": str(conversation_id),
            "content": message.content,
            "role": message.role,
            "created_at": message.created_at.isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error sending message to conversation {conversation_id}: {str(e)}")
        raise

async def process_previous_messages(conversation_id: UUID, user_id: UUID, db: Session, k_messages: int = 5) -> List[Dict[str, Any]]:
    """Process previous messages in a conversation."""
    
    logger.info(f"Processing previous messages for conversation {conversation_id} for user {user_id}")
    try:
        messages = await get_conversation_messages(conversation_id, user_id, db)
        return messages[-k_messages:]
    except Exception as e:
        logger.error(f"Error processing previous messages for conversation {conversation_id}: {str(e)}")
        raise

