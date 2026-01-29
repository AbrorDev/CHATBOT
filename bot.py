import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, FSInputFile, InputMediaDocument

from bot.config.config import BOT_TOKEN

from bot.handlers.register_handler import router as register_router
from bot.handlers.settings_handler import router as settings_router
from bot.handlers.chat_handler import router as chat_router

async def set_commands(bot: Bot):
    uz_commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="change", description="Tilni o‘zgartirish"),
    ]
    await bot.set_my_commands(uz_commands, language_code='uz')

    ru_commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="change", description="Изменить язык"),
    ]
    await bot.set_my_commands(ru_commands, language_code='ru')

    en_commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="change", description="Change language"),
    ]
    await bot.set_my_commands(en_commands, language_code='en')

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    dp.include_router(register_router)
    dp.include_router(settings_router)
    dp.include_router(chat_router)

    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Starting...")
    asyncio.run(main())