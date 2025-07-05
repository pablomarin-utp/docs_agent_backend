from app.chat.processor import process_message
from fastapi import APIRouter, Depends, HTTPException
from app.core.models import User, Conversation
from app.services.auth_service import  get_current_user
from app.services.conversation_service import get_user_conversations, create_conversation, update_conversation_summary
from app.services.messages_service import get_conversation_messages, send_message_to_conversation
from typing import List, Dict, Any
from app.core.database import get_db
from app.schemas.chat_schema import SendMessageRequest, CreateConversationRequest
from app.services.credit_service import deduct_credits
from app.chat.graph_workflow import agent
from sqlalchemy.orm import Session
import logging
from uuid import UUID

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/conversations")
async def get_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Endpoint to retrieve all conversations for a user.
    Requires a valid JWT and an active user account.
    """
    logger.info("Retrieving conversations for user: %s", user.id)

    try:
        conversations = await get_user_conversations(user.id, db)
        return conversations
    except Exception as e:
        logger.error(f"Error retrieving conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/conversations")
async def new_conversation(
    request: CreateConversationRequest,
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Endpoint to create a new conversation for a user.
    Requires a valid JWT and an active user account.
    """
    logger.info("Creating conversation for user")

    logger.debug(f"User ID: {user.id}, Title: {request.title}")

    try:
        conversation = await create_conversation(user.id, request.title, db)
        return conversation
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/conversations/{conversation_id}/messages")
async def retrieve_conversation_messages(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Endpoint to retrieve a specific conversation by ID for a user.
    Requires a valid JWT and an active user account.
    """
    logger.info(f"Retrieving messages for conversation {conversation_id} for user {user.id}")

    try:
        conversation_uuid = UUID(conversation_id)
        messages = await get_conversation_messages(conversation_uuid, user.id, db)
        if not messages:
            logger.warning(f"No messages found for conversation {conversation_id}")

        return messages
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    except Exception as e:
        logger.error(f"Error retrieving conversation messages {conversation_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Send a message in a specific conversation."""
    logger.info(f"Processing message for conversation {conversation_id} and user {user.id}")

    try:
        conversation_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")

    try:
        # Save user message first
        user_message = await send_message_to_conversation(
            conversation_id=conversation_uuid,
            role="user",
            content=request.content,
            db=db
        )

    except Exception as e:
        logger.error(f"[Bloque 1] Error verificando conversación o guardando mensaje del usuario: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al guardar el mensaje del usuario o cargar la conversación")

    try:
        # Process message and get conversation history
        messages = await process_message(
            conversation_id=conversation_uuid,
            user_id=user.id,
            new_input=request.content,
            db=db
        )
        
        # Invoke agent with the message history
        result = await agent.ainvoke({"messages": messages})

        # Extract the last message content
        full_state = result.get("messages", [])
        if full_state and hasattr(full_state[-1], 'content'):
            last = full_state[-1].content
        else:
            last = "No se pudo generar una respuesta"

    except Exception as e:
        logger.error(f"[Bloque 2] Error procesando mensaje con el agente: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar el mensaje con el agente")

    try:
        assistant_message = await send_message_to_conversation(
            conversation_id=conversation_uuid,
            role="assistant",
            content=last,
            db=db
        )

        credits_deducted = await deduct_credits(user.id, amount=1, db=db)

        return {"message": assistant_message, "credits_remaining": credits_deducted}

    except Exception as e:
        logger.error(f"[Bloque 3] Error guardando respuesta del asistente o actualizando resumen: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al guardar la respuesta o actualizar la conversación")

#-------------DEPRECATED ENDPOINTS----------------


"""
@router.post("/chat")
def chat(input_data: AgentState) -> dict:
    
    #Endpoint to handle user messages and return responses from the agent.
    
    logger.info("Received chat request")
    logger.debug(f"Input data: {input_data}")
    logger.debug(f"Received message from user {input_data.user_id}: {input_data.messages}")
    try:
        logger.debug(f"Processing message: {input_data.messages}")
        response = process_user_message(input_data.user_id, input_data.messages, graph, config)
        logger.info(f"Response for user {input_data.user_id}: {response}")
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""