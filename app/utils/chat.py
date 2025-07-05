from app.schemas.chat_schema import ChatMessage
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import ToolMessage
import logging

logger = logging.getLogger(__name__)

def convert_langchain_message(message) -> ChatMessage:
    """Convert a LangChain message to a ChatMessage."""
    try:
        if isinstance(message, ChatMessage):
            return message
            
        elif isinstance(message, AIMessage):
            return ChatMessage(
                role="assistant", 
                content=message.content or "", 
                tool_calls=getattr(message, "tool_calls", None)
            )
            
        elif isinstance(message, HumanMessage):
            return ChatMessage(
                role="user", 
                content=message.content or "", 
                tool_calls=getattr(message, "tool_calls", None)
            )
            
        elif isinstance(message, SystemMessage):
            return ChatMessage(
                role="system", 
                content=message.content or ""
            )
            
        elif isinstance(message, ToolMessage):
            return ChatMessage(
                role="tool", 
                content=message.content or ""
            )
            
        elif isinstance(message, dict):
            return ChatMessage(**message)
            
        else:
            logger.warning(f"Unsupported message type: {type(message)}")
            return ChatMessage(
                role="assistant", 
                content=str(message)
            )
            
    except Exception as e:
        logger.error(f"Error converting message: {str(e)}")
        return ChatMessage(
            role="assistant", 
            content="Error processing message"
        )