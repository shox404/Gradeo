from data.config import ADMINS
from aiogram.types import Message


async def is_admin(message: Message):
    """Checks if the user is an admin."""
    for admin in ADMINS:
        return message.from_user.id == int(admin)
