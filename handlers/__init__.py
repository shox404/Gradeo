from app import dp
from handlers.start import start_router
from handlers.manage_users.manage_users import manage_users_router
from handlers.manage_users.add_user import add_user_router
from handlers.manage_users.edit_user import edit_user_router
from handlers.manage_users.delete_user import delete_user_router

dp.include_router(start_router)
dp.include_router(manage_users_router)
dp.include_router(add_user_router)
dp.include_router(edit_user_router)
dp.include_router(delete_user_router)
