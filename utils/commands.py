from aiogram.types import BotCommand
from loader import bot


async def set_admin_commands():
    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="Приветственное сообщение"),
            BotCommand(command="manage_classes", description="Управление классами"),
            BotCommand(command="manage_users", description="Управление пользователями"),
            BotCommand(command="manage_subjects", description="Управление предметами"),
        ]
    )


async def set_teacher_commands():
    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="Приветственное сообщение"),
            BotCommand(command="estimate_student", description="Оценивать студента"),
            BotCommand(command="notify_class", description="Уведомление класса"),
        ]
    )


async def set_student_commands():
    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="Приветственное сообщение"),
            BotCommand(command="view_marks", description="Просмотр оценок"),
        ]
    )
