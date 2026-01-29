from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.settings_keyboard import settings_language_keyboard

from database.database import update_user_lang

router = Router()

TEXTS = {
    "uz": "✅ Til muvaffaqiyatli o‘zgartirildi",
    "ru": "✅ Язык успешно изменён"
}

@router.message(Command("change"))
async def change_language(message: Message, state: FSMContext):
    text = "Tilni tanlang:\n\nВыберите язык:"

    await state.set_state("SettingsState:language")
    await message.answer(text, reply_markup=settings_language_keyboard())

@router.callback_query(F.data.startswith("settings_lang_"))
async def set_new_language(call: CallbackQuery, state: FSMContext):
    lang = call.data.split("_")[-1]

    await update_user_lang(call.from_user.id, lang)

    await state.update_data(lang=lang)
    await state.clear()

    await call.message.edit_text(TEXTS[lang])