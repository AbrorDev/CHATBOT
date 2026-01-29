

from config import USE_ADMIN_FILTER, ADMINS

def is_admin(user_id: int) -> bool:
    if not USE_ADMIN_FILTER:
        return True  # hamma kiraveradi
    return user_id in ADMINS