from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from utils.detect_admin import is_admin
from keyboards.inline.users import (
    manage_user_keyboard,
    edit_user_keyboard,
    delete_user_keyboard,
)

manage_users_router = Router()


@manage_users_router.message(Command("manage_users"))
async def manage_users(message: Message):
    if await is_admin(message):
        await message.answer(
            "<b>Choose an option to manage users</b>", reply_markup=manage_user_keyboard
        )
    else:
        await message.answer("⛔ You don't have permission to use this command.")


@manage_users_router.callback_query(lambda c: c.data == "edit_user")
async def edit_user(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "<b>Choose what you want to edit</b>", reply_markup=edit_user_keyboard
    )
    await callback_query.answer()


@manage_users_router.callback_query(lambda c: c.data == "delete_user")
async def edit_user(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "<b>Choose what you want to delete</b>", reply_markup=delete_user_keyboard
    )
    await callback_query.answer()


@manage_users_router.callback_query(lambda c: c.data == "back_to_manage_users")
async def back_to_manage_users(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "<b>Choose an option to manage users</b>", reply_markup=manage_user_keyboard
    )
    await callback_query.answer()
