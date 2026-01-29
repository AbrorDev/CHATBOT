import os
from dotenv import load_dotenv

from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMINS = [int(x) for x in os.getenv("TELEGRAM_ADMINS", "").split(",") if x.strip()]
USE_ADMIN_FILTER = os.getenv("USE_ADMIN_FILTER", "True").lower() == "true"

# bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))