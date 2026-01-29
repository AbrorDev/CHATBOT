import asyncio
from config.settings import SYSTEM_PROMPT_UZ, SYSTEM_PROMPT_RU
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from database.database import get_last_messages, get_language
from agent.agent import rag_agent
from datetime import datetime, timedelta

async def answer_question(text, cfg):
    user_id = cfg["configurable"]["tg_id"]
    user_text = text

    language = await get_language(user_id)

    messages = []

    if language[0]["lang"] == "uz":
        messages.append(SystemMessage(content=SYSTEM_PROMPT_UZ))
        user_query = f"{user_text}\n\nJavobni menga o'zbek tilida bering."
    else:
        messages.append(SystemMessage(content=SYSTEM_PROMPT_RU))
        user_query = f"{user_text}\n\nДайте мне ответ на русском языке."

    one_day_ago = (datetime.now() - timedelta(hours=24)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    user_messages = await get_last_messages(user_id, one_day_ago, 3)

    if user_messages:
        user_messages.reverse()
        for m in user_messages:
            messages.append(HumanMessage(content=m["content"]))
            messages.append(AIMessage(content=m["answer"]))

    messages.append(HumanMessage(content=user_query))

    t = await rag_agent.ainvoke(
        {
            "messages": messages
        },
        config=cfg
    )
    return t['messages'][-1].content

async def main(query, tg_id):
    cfg = {"configurable": {"tg_id": tg_id}}
    result = await answer_question(query, cfg)
    print(result)

if __name__ == "__main__":
    asyncio.run(main("qanaqa kartalar bor",994282938)) # 994282938