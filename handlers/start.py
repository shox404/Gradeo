from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram import Router
from utils.commands import (
    set_admin_commands,
    set_teacher_commands,
    set_student_commands,
)
from utils.detect_admin import is_admin
from data.config import ADMINS
from app import bot
from firebase.functions.users import get_user_data

start_router = Router()


@start_router.message(CommandStart())
async def start(message: Message):
    user = await get_user_data(message.from_user.id)

    if await is_admin(message):
        await set_admin_commands()
    elif user and user["role"] == "Teacher":
        await set_teacher_commands()
    elif user and user["role"] == "Student":
        await set_student_commands()
    elif not user:
        for admin in ADMINS:
            user = message.from_user
            full_name = f"{user.first_name} {user.last_name if user.last_name is not None else ""}"
            data = f"<b>Full Name: <i>{full_name}</i></b>\n<b>ID: <i>{user.id}</i></b> \n<b>User Name: <i>@{user.username}</i></b>"
            await bot.send_message(admin, data)
    await message.answer(f"Salom, {message.from_user.full_name}!")
