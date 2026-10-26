from sqlalchemy.orm import DeclarativeBase


class PhonesBase(DeclarativeBase):
    """Metadata of `modules/phones` only: the module owns its tables. Connection: `core.database`."""
