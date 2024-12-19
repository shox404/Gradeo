from app import dp
from handlers.start import start_router

dp.include_router(start_router)

# users
from handlers.manage_users.main import manage_users_router
from handlers.manage_users.add_user import add_user_router
from handlers.manage_users.delete_student import delete_student_router
from handlers.manage_users.delete_teacher import delete_teacher_router
from handlers.manage_users.edit_teacher import edit_teacher_router
from handlers.manage_users.edit_student import edit_student_router

dp.include_router(manage_users_router)
dp.include_router(add_user_router)
dp.include_router(edit_student_router)
dp.include_router(edit_teacher_router)
dp.include_router(delete_student_router)
dp.include_router(delete_teacher_router)

# classes
from handlers.manage_classes.main import manage_classes_router
from handlers.manage_classes.add_class import add_class_router
from handlers.manage_classes.edit_class import edit_class_router
from handlers.manage_classes.delete_class import delete_class_router

dp.include_router(manage_classes_router)
dp.include_router(add_class_router)
dp.include_router(edit_class_router)
dp.include_router(delete_class_router)

# marks
from handlers.estimate_student.main import estimate_student_router
from handlers.estimate_student.set_mark import set_mark_router
from handlers.estimate_student.delete_mark import delete_mark_router
from handlers.view_marks.main import view_marks_router
from handlers.view_marks.view_daily_marks import view_daily_marks_router

dp.include_router(estimate_student_router)
dp.include_router(set_mark_router)
dp.include_router(delete_mark_router)
dp.include_router(view_marks_router)
dp.include_router(view_daily_marks_router)
