from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.keyboards.register_keyboard import language_keyboard, phone_keyboard
from bot.states.register_state import RegisterState

from database.database import save_user, get_language

router = Router()

TEXTS = {
    "uz": {
        "choose_lang": "Tilni tanlang:",
        "send_phone": "📱 Telefon raqamingizni yuboring:",
        "welcome": "Assalomu alaykum! Sizga qanday yordam bera olaman?"
    },
    "ru": {
        "choose_lang": "Выберите язык:",
        "send_phone": "📱 Отправьте номер телефона:",
        "welcome": "Здравствуйте! Чем могу вам помочь?"
    }
}

START_TEXTS = {
    "uz": "Assalomu alaykum. Sizga qanday yordam bera olaman?",
    "ru": "Здравствуйте. Чем я могу вам помочь?"
}

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    lang = await get_language(message.from_user.id)

    if lang:
        await message.answer(START_TEXTS[lang[0]['lang']])
    else:
        await state.set_state(RegisterState.language)
        await message.answer(
            "Tilni tanlang\n\nВыберите язык",
            reply_markup=language_keyboard()
        )

@router.callback_query(RegisterState.language, F.data.startswith("lang_"))
async def set_language(call: CallbackQuery, state: FSMContext):
    lang = call.data.split("_")[1]

    await state.update_data(lang=lang)
    await state.set_state(RegisterState.phone)

    await call.message.edit_text(TEXTS[lang]["send_phone"])
    await call.message.answer(
        TEXTS[lang]["send_phone"],
        reply_markup=phone_keyboard()
    )

@router.message(RegisterState.phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    phone_number = message.contact.phone_number
    await save_user(lang, message.from_user.id, phone_number)

    await state.clear()

    await message.answer(
        TEXTS[lang]["welcome"],
        reply_markup=None
    )