from pydantic import BaseModel
from typing import List, Literal, Optional
from langchain.schema import BaseMessage
from langgraph.prebuilt.chat_agent_executor import AgentState as LGAgentState

END = "end"

class SendMessageRequest(BaseModel):
    """Request schema for sending a message to a conversation."""
    content: str

class AgentState(LGAgentState):
    """Extended agent state with conversation summary."""
    summary: Optional[str]

class CreateConversationRequest(BaseModel):
    """Request schema for creating a new conversation."""
    title: str = "New Conversation"