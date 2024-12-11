from app import dp
from handlers.start import start_router
from handlers.add_user import add_user_router
from handlers.add_class import add_class_router
from handlers.edit_user import edit_user_router
 
dp.include_router(start_router)
dp.include_router(add_user_router)
dp.include_router(add_class_router)
dp.include_router(edit_user_router)