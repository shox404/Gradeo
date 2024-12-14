from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.detect_admin import is_admin
from keyboards.inline.classes import manage_classes_keyboard

manage_classes_router = Router()


@manage_classes_router.message(Command("manage_classes"))
async def manage_classes(message: Message):
    if await is_admin(message):
        await message.answer(
            "<b>Choose an option to manage classes</b>",
            reply_markup=manage_classes_keyboard,
        )
    else:
        await message.answer("⛔ You don't have permission to use this command.")
