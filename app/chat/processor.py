from app.schemas.chat_schema import AgentState
from fastapi import HTTPException
from app.services.messages_service import get_conversation_messages
from app.services.conversation_service import get_conversation_by_id
from app.core.models import Conversation
from sqlalchemy.orm import Session
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


async def build_conversation_history(conversation: Conversation, user_id: UUID, db: Session) -> list:

    """
    Build the conversation history for a specific conversation.
    """

    messages = []

    if conversation.summary:
        messages.append({
            "role": "system",
            "content": f"Resumen hasta ahora: {conversation.summary}"
        })

    last_messages = await get_conversation_messages(conversation.id, user_id, db=db)

    for msg in last_messages:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
            # ✅ Remove any date-related fields from messages
        })

    return messages

async def process_message(user_id: UUID, conversation_id: UUID, new_input: str, db: Session) -> tuple:
    """
    Process a user message and return the response from the agent.
    """
    logger.info(f"Processing message for user {user_id}")

    try:

        conversation = await get_conversation_by_id(conversation_id, user_id, db=db)

        messages = await build_conversation_history(
            conversation=conversation,
            user_id=user_id,
            db=db
        )

        logger.debug(f"Built conversation history for user {user_id}: {messages}")

        return messages

    except Exception as e:
        logger.error(f"Error processing message for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing message")