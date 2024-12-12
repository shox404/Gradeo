from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.detect_admin import is_admin
from keyboards.inline.manage_user_keyboard import manage_user_keyboard

manage_users_router = Router()


@manage_users_router.message(Command("manage_users"))
async def manage_users(message: Message):
    if await is_admin(message):
        await message.answer(
            "<b>Choose an option to manage users</b>", reply_markup=manage_user_keyboard
        )
    else:
        await message.answer("⛔ You don't have permission to use this command.")
