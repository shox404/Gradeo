from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.detect_admin import is_admin
from keyboards.inline.classes import manage_subjects_keyboard

manage_subjects_router = Router()


@manage_subjects_router.message(Command("manage_subjects"))
async def manage_classes(message: Message):
    if await is_admin(message):
        await message.answer(
            "<b>Выберите действие для управления предметами.</b>",
            reply_markup=manage_subjects_keyboard,
        )
    else:
        await message.answer("⛔ У вас нет прав для использования этой команды.")
