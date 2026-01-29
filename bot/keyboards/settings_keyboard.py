from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def settings_language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇺🇿 O'zbekcha",
                    callback_data="settings_lang_uz"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇷🇺 Русский",
                    callback_data="settings_lang_ru"
                )
            ]
        ]
    )