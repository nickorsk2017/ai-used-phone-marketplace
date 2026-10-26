"""Public interface of `modules/auth`: docs/backend/AUTH.md#session-token.

The module has no tables and no settings: the secret is passed by `modules/main`. It calls only `users.services`:
docs/backend/DESIGN.md#modules.
"""

from modules.auth.services.access import authenticate, is_owner
from modules.auth.services.token import issue_token, verify_token

__all__ = ["authenticate", "is_owner", "issue_token", "verify_token"]
