from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from utils.detect_admin import is_admin
from firebase.functions.classes import get_all_classes

view_classes_router = Router()


@view_classes_router.callback_query(lambda c: c.data == "view_classes")
async def view_classes_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        classes = await get_all_classes()

        if not classes:
            await callback_query.message.answer("❌ No classes found.")
            return

        class_list = "\n".join(
            [
                f"📚 {class_data['name']} (Teacher: {class_data['teacher']})"
                for class_data in classes
            ]
        )

        await callback_query.message.answer(f"<b>Classes</b>\n{class_list}")
    else:
        await callback_query.message.answer(
            "⛔ You don't have permission to use this command."
        )

    await callback_query.answer()
