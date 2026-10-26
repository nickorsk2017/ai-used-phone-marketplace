"""Public interface of `modules/phones`. Called by `modules/main`: docs/backend/DESIGN.md#modules."""

from modules.phones.services.ai import check_listing, generate_description
from modules.phones.services.crud import create_phone, list_user_phones

__all__ = ["check_listing", "create_phone", "generate_description", "list_user_phones"]
