from langgraph.graph import StateGraph, END, START
from app.schemas.chat_schema import AgentState
from app.config.llm import llm_model
from app.chat.tools import tools_list
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from app.utils.logging_utils import get_secure_logger

logger = get_secure_logger(__name__)

# Summary prompt template for conversation summarization
summary_prompt = PromptTemplate(
    input_variables=["chat_history"],
    template="Conversation summary:\n{chat_history}\n\nSummary:"
)

# Chain for generating conversation summaries
summary_chain = LLMChain(
    llm=llm_model,
    prompt=summary_prompt
)

def summary_hook(state: AgentState):
    """
    Hook to summarize conversation when it gets too long.
    
    Args:
        state: Current agent state with messages
        
    Returns:
        Updated state with summary and trimmed messages
    """
    msgs = state["messages"]
    
    # Summarize if conversation has more than 10 messages
    if len(msgs) > 10:  
        logger.debug("Summarizing conversation", message_count=len(msgs))
        
        # Get text from last 10 messages for summary
        chat_str = "\n".join(m.content for m in msgs[-10:])
        summary = summary_chain.run(chat_history=chat_str)
        
        # Keep summary as system message + last 5 messages
        new_messages = [SystemMessage(content=f"Summary so far: {summary}")] + msgs[-5:]
        
        logger.debug("Conversation summarized", original_count=len(msgs), new_count=len(new_messages))
        return {"messages": new_messages, "summary": summary}
    
    return {}  # No changes needed

# Create the main agent with tools and summarization
agent = create_react_agent(
    model=llm_model.bind_tools(tools_list),
    tools=tools_list,
    pre_model_hook=summary_hook,
    state_schema=AgentState
)

