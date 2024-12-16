from aiogram.types import BotCommand
from loader import bot


async def set_admin_commands():
    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="Sinf qo'shish"),
            BotCommand(command="manage_classes", description="Sinf qo'shish"),
            BotCommand(command="manage_users", description="Foydalanuvchi qo'shish"),
            BotCommand(command="assign_subject", description="Fanlarni biriktirish"),
            BotCommand(command="view_reports", description="Hisobotlarni ko'rish"),
        ]
    )


async def set_teacher_commands():
    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="Sinf qo'shish"),
            BotCommand(command="set_mark", description="Uquvchini baholash"),
        ]
    )
