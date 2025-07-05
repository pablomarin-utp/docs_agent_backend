from langgraph.graph import StateGraph, END, START
from app.schemas.chat_schema import AgentState
from app.config.llm import llm_model
from app.chat.tools import tools_list
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
import logging
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)
summary_prompt = PromptTemplate(
    input_variables=["chat_history"],
    template="Resumen de la conversación:\n{chat_history}\n\nResumen:"
)
summary_chain = LLMChain(
    llm=llm_model,
    prompt=summary_prompt
)

def summary_hook(state: AgentState):
    msgs = state["messages"]
    if len(msgs) > 10:  
        chat_str = "\n".join(m.content for m in msgs[-10:])
        summary = summary_chain.run(chat_history=chat_str)
        new_messages = [SystemMessage(content=f"Resumen hasta ahora: {summary}")] + msgs[-5:]
        return {"messages": new_messages, "summary": summary}
    return {}  


agent = create_react_agent(
    model=llm_model.bind_tools(tools_list),
    tools=tools_list,
    pre_model_hook=summary_hook,
    state_schema=AgentState
)

