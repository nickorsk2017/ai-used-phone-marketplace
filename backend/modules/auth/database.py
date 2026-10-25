from sqlalchemy.orm import DeclarativeBase


class AuthBase(DeclarativeBase):
    """Metadata of `modules/auth` only: the module owns its tables. Connection: `core.database`."""
