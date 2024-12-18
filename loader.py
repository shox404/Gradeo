import logging
from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from data import config
from aiogram.client.bot import DefaultBotProperties

logging.basicConfig(level=logging.INFO)
bot = Bot(
    token=config.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

