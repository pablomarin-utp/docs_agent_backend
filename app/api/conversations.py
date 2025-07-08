from app.chat.processor import process_message
from fastapi import APIRouter, Depends, HTTPException
from app.core.models import User, Conversation
from app.services.auth_service import  get_current_user
from app.services.conversation_service import get_user_conversations, create_conversation, delete_conversation_service
from app.services.messages_service import get_conversation_messages, send_message_to_conversation
from typing import List, Dict, Any
from app.core.database import get_db
from app.schemas.chat_schema import SendMessageRequest, CreateConversationRequest
from app.services.credit_service import deduct_credits
from app.chat.graph_workflow import agent
from sqlalchemy.orm import Session
from uuid import UUID
from app.utils.logging_utils import get_secure_logger

logger = get_secure_logger(__name__)
router = APIRouter()

@router.get("/conversations")
async def get_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Endpoint to retrieve all conversations for a user."""
    logger.info("Retrieving conversations for user", user_id=user.id)

    try:
        conversations = await get_user_conversations(user.id, db)
        logger.info("Conversations retrieved successfully", user_id=user.id, count=len(conversations))
        return conversations
    except Exception as e:
        logger.error("Error retrieving conversations", user_id=user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/conversations")
async def new_conversation(
    request: CreateConversationRequest,
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Endpoint to create a new conversation for a user."""
    logger.info("Creating new conversation", user_id=user.id, title=request.title)

    try:
        conversation = await create_conversation(user.id, request.title, db)
        logger.info("Conversation created successfully", user_id=user.id, conversation_id=conversation["id"])
        return conversation
    except Exception as e:
        logger.error("Error creating conversation", user_id=user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/conversations/{conversation_id}/messages")
async def retrieve_conversation_messages(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Endpoint to retrieve a specific conversation by ID for a user."""
    logger.info("Retrieving messages for conversation", conversation_id=conversation_id, user_id=user.id)

    try:
        conversation_uuid = UUID(conversation_id)
        messages = await get_conversation_messages(conversation_uuid, user.id, db)
        
        logger.info("Messages retrieved successfully", conversation_id=conversation_id, user_id=user.id, count=len(messages))
        return messages
    except ValueError:
        logger.warning("Invalid conversation ID format", conversation_id=conversation_id, user_id=user.id)
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    except Exception as e:
        logger.error("Error retrieving conversation messages", conversation_id=conversation_id, user_id=user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Send a message in a specific conversation."""
    logger.info("Processing message for conversation", conversation_id=conversation_id, user_id=user.id, content=request.content)

    try:
        conversation_uuid = UUID(conversation_id)
    except ValueError:
        logger.warning("Invalid conversation ID format", conversation_id=conversation_id, user_id=user.id)
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")

    try:
        # Save user message first
        user_message = await send_message_to_conversation(
            conversation_id=conversation_uuid,
            role="user",
            content=request.content,
            db=db
        )
        logger.debug("User message saved", message_id=user_message["id"], conversation_id=conversation_id)

    except Exception as e:
        logger.error("Error saving user message", conversation_id=conversation_id, user_id=user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Error al guardar el mensaje del usuario")

    try:
        # Process message and get conversation history
        messages = await process_message(
            conversation_id=conversation_uuid,
            user_id=user.id,
            new_input=request.content,
            db=db
        )
        
        logger.debug("Message processed, invoking agent", conversation_id=conversation_id, user_id=user.id)
        
        # Invoke agent with the message history
        result = await agent.ainvoke({"messages": messages})

        # Extract the last message content
        full_state = result.get("messages", [])
        if full_state and hasattr(full_state[-1], 'content'):
            assistant_response = full_state[-1].content
        else:
            assistant_response = "No se pudo generar una respuesta"
            
        logger.debug("Agent response generated", conversation_id=conversation_id, user_id=user.id)

    except Exception as e:
        logger.error("Error processing message with agent", conversation_id=conversation_id, user_id=user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Error al procesar el mensaje con el agente")

    try:
        assistant_message = await send_message_to_conversation(
            conversation_id=conversation_uuid,
            role="assistant",
            content=assistant_response,
            db=db
        )

        credits_deducted = await deduct_credits(user.id, amount=1, db=db)

        logger.info("Message processed successfully", conversation_id=conversation_id, user_id=user.id, credits_deducted=credits_deducted)
        return {"message": assistant_message, "credits_remaining": credits_deducted}

    except Exception as e:
        logger.error("Error saving assistant response", conversation_id=conversation_id, user_id=user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Error al guardar la respuesta del asistente")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, bool]:
    """Endpoint to delete a specific conversation by ID for a user."""
    logger.info("Deleting conversation", conversation_id=conversation_id, user_id=user.id)

    try:
        conversation_uuid = UUID(conversation_id)
        await delete_conversation_service(conversation_uuid, user.id, db)
        logger.info("Conversation deleted successfully", conversation_id=conversation_id, user_id=user.id)
        return {"message": True}
    except ValueError:
        logger.warning("Invalid conversation ID format", conversation_id=conversation_id, user_id=user.id)
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    except Exception as e:
        logger.error("Error deleting conversation", conversation_id=conversation_id, user_id=user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


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