from aiogram.types import BotCommand
from loader import bot


async def set_admin_commands():
    await bot.set_my_commands(
        commands=[
            BotCommand(command="add_user", description="Foydalanuvchi qo'shish"),
            BotCommand(command="add_class", description="Sinf qo'shish"),
            BotCommand(command="assign_subject", description="Fanlarni biriktirish"),
            BotCommand(command="view_reports", description="Hisobotlarni ko'rish"),
            BotCommand(
                command="edit_user", description="Foydalanuvchilarni tahrirlash"
            ),
        ]
    )


async def set_teacher_commands():
    await bot.set_my_commands(
        commands=[
            BotCommand(command="set_mark", description="Uquvchini baholash"),
        ]
    )
