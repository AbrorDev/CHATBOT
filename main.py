from fastapi import FastAPI
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from database.database import get_language, get_last_messages
from agent.agent import rag_agent

from config.settings import SYSTEM_PROMPT_UZ, SYSTEM_PROMPT_RU

from app.response_schema import ChatResponse, ChatRequest, FileResponse

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    user_id = req.user_id
    user_text = req.text

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

    cfg = {"configurable": {"tg_id": user_id}}

    result = await rag_agent.ainvoke(
        {"messages": messages},
        config=cfg
    )

    answer_text = result["messages"][-1].content

    if result.get("outbox"):
        files = []
        for f in result["outbox"]:
            files.append(
                FileResponse(
                    path=f["path"],
                    name=f.get("name")
                )
            )

        return ChatResponse(
            answer=answer_text,
            files=files
        )

    return ChatResponse(answer=answer_text)

# import asyncio
# from config.settings import SYSTEM_PROMPT_UZ
# from langchain_core.messages import HumanMessage, SystemMessage
# from agent.agent import rag_agent
#
# async def terst(text, cfg):
#     t = await rag_agent.ainvoke(
#         {
#             "messages": [
#                 SystemMessage(content=SYSTEM_PROMPT_UZ),
#                 HumanMessage(content=text)
#             ]
#         },
#         config=cfg
#     )
#     return t['messages'][-1].content
#
# async def main(query, tg_id):
#     cfg = {"configurable": {"tg_id": tg_id}}
#     result = await terst(query, cfg)
#     print(result)
#
# if __name__ == "__main__":
#     asyncio.run(main("qanaqa kartalar bor",994282938))