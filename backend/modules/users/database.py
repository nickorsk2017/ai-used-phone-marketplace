from sqlalchemy.orm import DeclarativeBase


class UsersBase(DeclarativeBase):
    """Metadata of `modules/users` only: the module owns its tables. Connection: `core.database`."""
