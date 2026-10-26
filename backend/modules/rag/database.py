from sqlalchemy.orm import DeclarativeBase


class RagBase(DeclarativeBase):
    """Metadata of `modules/rag` only: the module owns its tables. Connection: `core.database`."""
