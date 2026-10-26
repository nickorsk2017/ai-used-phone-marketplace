"""Session token of `modules/auth`: Python standard library only, no database."""

import base64
import hashlib
import hmac
import uuid

TOKEN_SEPARATOR = "."


def _signature(user_id: str, secret: str) -> str:
    digest = hmac.new(secret.encode(), user_id.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def issue_token(user_id: uuid.UUID, secret: str) -> str:
    """`<user_id>.<signature>`, no expiration."""
    value = str(user_id)
    return f"{value}{TOKEN_SEPARATOR}{_signature(value, secret)}"


def verify_token(token: str | None, secret: str) -> uuid.UUID | None:
    """The user ID of a token with a valid signature. `None` for any missing or malformed token."""
    if not token:
        return None
    value, separator, signature = token.partition(TOKEN_SEPARATOR)
    if not separator or not hmac.compare_digest(signature.encode(), _signature(value, secret).encode()):
        return None
    try:
        return uuid.UUID(value)
    except ValueError:
        return None
