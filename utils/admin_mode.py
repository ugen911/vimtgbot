# utils/admin_mode.py

# Простая in-memory структура: {user_id: True/False}
admin_mode = {}


def enable_admin(user_id: int):
    admin_mode[user_id] = True


def disable_admin(user_id: int):
    admin_mode[user_id] = False


def is_admin_mode(user_id: int) -> bool:
    return admin_mode.get(user_id, False)
