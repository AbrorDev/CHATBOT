from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence, List, Dict
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage, AIMessage
from operator import add as add_messages
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

import pandas as pd
from datetime import datetime, timedelta

from database.database import get_last_messages, get_language
from config.settings import (client,
                             contextualize_q_system_prompt_uz,
                             contextualize_q_system_prompt_ru,
                             OPENAI_API_KEY,
                             MODEL_NAME,
                             vector_store_id_uz,
                             vector_store_id_ru)
from dotenv import load_dotenv

load_dotenv()

async def retrieve(query: str, config: RunnableConfig) -> str:
    """Retrieve information related to a query.
    query: user question
    tg_id: user telegram id """
    tg_id = (config.get("configurable") or {}).get("tg_id")
    language = await get_language(tg_id)
    if language[0]["lang"] == "uz":
        sr = await client.vector_stores.search(
            vector_store_id=vector_store_id_uz,
            query=query,
            max_num_results=3
        )
    else:
        sr = await client.vector_stores.search(
            vector_store_id=vector_store_id_ru,
            query=query,
            max_num_results=2
        )
    return "\n\n".join([doc.content[0].text for doc in sr.data])

@tool
async def get_history(user_query, config: RunnableConfig) -> str:
    """this function generate question depend on chat history"""
    tg_id = (config.get("configurable") or {}).get("tg_id")
    language = await get_language(tg_id)

    one_day_ago = (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")

    user_messages = await get_last_messages(tg_id, one_day_ago, 3)
    history_ = list()
    if user_messages:
        user_messages.reverse()
        for i in user_messages:
            history_.append(HumanMessage(content=i['content']))
            history_.append(AIMessage(i['answer']))


    if language[0]['lang'] == "uz":
        contextualize_q_system_prompt = contextualize_q_system_prompt_uz
        user_query = f"{user_query}\n\nJavobni menga o'zbek tilida bering."
    else:
        contextualize_q_system_prompt = contextualize_q_system_prompt_ru
        user_query = f"{user_query}\n\nДайте мне ответ на русском языке."

    history_.append(HumanMessage(content=user_query))

    messages = [SystemMessage(content=contextualize_q_system_prompt)] + history_

    llm_generate_question = ChatOpenAI(model=MODEL_NAME, temperature = 0, api_key=OPENAI_API_KEY)

    response = llm_generate_question.invoke(messages)

    print(response.content)

    result = await retrieve(response.content, config)
    return result

tools = [get_history]

llm = ChatOpenAI(model=MODEL_NAME, temperature = 0, api_key=OPENAI_API_KEY).bind_tools(tools)

def concat_list(prev, new):
    return (prev or []) + (new or [])

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    outbox: Annotated[List[Dict], concat_list]

def should_continue(state: AgentState):
    """Check if the last message contains tool calls."""
    result = state['messages'][-1]
    return hasattr(result, 'tool_calls') and len(result.tool_calls) > 0

tools_dict = {our_tool.name: our_tool for our_tool in tools} # Creating a dictionary of our tools

async def call_llm(state: AgentState, config: RunnableConfig):
    response = await llm.ainvoke(state['messages'])

    return {"messages": [response]} # AIMessage(content=response.content)

async def take_action(state: AgentState, config: RunnableConfig) -> AgentState:
    """Execute tool calls from the LLM's response."""

    tool_calls = state['messages'][-1].tool_calls
    tg_id = (config.get("configurable") or {}).get("tg_id")

    out_files: List[Dict] = []
    new_message = list()
    for t in tool_calls:
        name = t['name']
        args = t['args']
        print(f"Calling Tool: {t['name']} with query: {t['args']}") # .get('query', 'No query provided')

        if not t['name'] in tools_dict: # Checks if a valid tool is present
            print(f"\nTool: {t['name']} does not exist.")
            result = "Incorrect Tool Name, Please Retry and Select tool from List of Available tools."

        else:
            result = await tools_dict[name].ainvoke({**args, "tg_id": tg_id})

            # LLM uchun faqat matn
            reply_text = result.get("reply") if isinstance(result, dict) else str(result)

            # Outboxga fayllarni yig'amiz
            if isinstance(result, dict) and "_file" in result:
                out_files.append(result["_file"])

            # Appends the Tool Message
            new_message = ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(reply_text))

    print("Tools Execution Complete. Back to the model!")
    if out_files:
        state["outbox"] = out_files

    return {'messages': [new_message], 'outbox': state['outbox']}

graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("retriever_agent", take_action)

graph.add_conditional_edges(
    "llm",
    should_continue,
    {True: "retriever_agent", False: END}
)
graph.add_edge("retriever_agent", "llm")
graph.set_entry_point("llm")

rag_agent = graph.compile()