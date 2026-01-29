import os
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, InputMediaDocument

from database.database import save_message
# from config.functions import ask_ai
from test import answer_question

router = Router()

TEXTS = {
    "uz": {
        "sent": "📨 Xabaringiz adminga yuborildi"
    },
    "ru": {
        "sent": "📨 Ваше сообщение отправлено администратору"
    }
}

@router.message()
async def handle_user_message(message: Message):
    # result = await ask_ai(message.from_user.id, message.text)
    cfg = {"configurable": {"tg_id": message.from_user.id}}
    result = await answer_question(message.text, cfg)
    if result.get("outbox"):
        file_paths = result['files']

        files = []
        if len(file_paths) > 1:
            for i, f in enumerate(file_paths):
                if i < len(file_paths) - 1:
                    files.append(InputMediaDocument(
                        media=FSInputFile(f[0], filename=f[1])
                    ))
                else:
                    files.append(InputMediaDocument(
                        media=FSInputFile(f[0], filename=f[1]),
                        caption=result['messages'][-1].content
                    ))
            await message.answer_media_group(media=files)
            for f in file_paths:
                os.remove(f[0])
        else:
            await message.answer_document(FSInputFile(file_paths[0][0]), caption=result['answer'])
    else:
        await message.answer(result['answer'])

        await save_message(message.text, result['answer'], message.from_user.id)