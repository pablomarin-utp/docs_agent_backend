from app.schemas.chat_schema import AgentState
from fastapi import HTTPException
from app.services.messages_service import get_conversation_messages
from app.services.conversation_service import get_conversation_by_id
from app.core.models import Conversation
from sqlalchemy.orm import Session
from uuid import UUID
from app.utils.logging_utils import get_secure_logger

logger = get_secure_logger(__name__)

async def build_conversation_history(conversation: Conversation, user_id: UUID, db: Session) -> list:
    """Build the conversation history for a specific conversation."""
    logger.debug("Building conversation history", conversation_id=conversation.id, user_id=user_id)
    
    messages = []

    if conversation.summary:
        messages.append({
            "role": "system",
            "content": f"Resumen hasta ahora: {conversation.summary}"
        })
        logger.debug("Added conversation summary to history", conversation_id=conversation.id)

    try:
        last_messages = await get_conversation_messages(conversation.id, user_id, db=db)
        
        for msg in last_messages:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        logger.debug("Conversation history built successfully", conversation_id=conversation.id, message_count=len(messages))
        return messages
        
    except Exception as e:
        logger.error("Error building conversation history", conversation_id=conversation.id, user_id=user_id, error=str(e))
        raise

async def process_message(user_id: UUID, conversation_id: UUID, new_input: str, db: Session) -> tuple:
    """Process a user message and return the response from the agent."""
    logger.info("Processing message", user_id=user_id, conversation_id=conversation_id, content=new_input)

    try:
        conversation = await get_conversation_by_id(conversation_id, user_id, db=db)
        
        if not conversation:
            logger.warning("Conversation not found", conversation_id=conversation_id, user_id=user_id)
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = await build_conversation_history(
            conversation=conversation,
            user_id=user_id,
            db=db
        )

        logger.debug("Message processing completed", user_id=user_id, conversation_id=conversation_id)
        return messages

    except Exception as e:
        logger.error("Error processing message", user_id=user_id, conversation_id=conversation_id, error=str(e))
        raise HTTPException(status_code=500, detail="Error processing message")