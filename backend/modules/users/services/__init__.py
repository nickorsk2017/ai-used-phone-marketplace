"""Public interface of `modules/users`. Called by `modules/main` and `modules/auth`: docs/backend/DESIGN.md#modules."""

from modules.users.services.crud import create_user, get_user, update_user

__all__ = ["create_user", "get_user", "update_user"]
