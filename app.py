import asyncio
import handlers
from loader import dp, bot


async def start():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
