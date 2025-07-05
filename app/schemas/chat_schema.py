from pydantic import BaseModel
from typing import List, Literal, Optional
from langchain.schema import BaseMessage
from langgraph.prebuilt.chat_agent_executor import AgentState as LGAgentState

END = "end"

class SendMessageRequest(BaseModel):
    content: str

class AgentState(LGAgentState):
    summary: Optional[str]

class CreateConversationRequest(BaseModel):
    title: str = "New Conversation"