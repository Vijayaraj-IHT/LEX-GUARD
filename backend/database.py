"""Database engine, session factory, and schema initialisation."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from backend.config import get_settings

settings = get_settings()

# SQLite needs check_same_thread=False for FastAPI
connect_args = {}
if settings.lexguard_db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.lexguard_db_url,
    connect_args=connect_args,
    echo=settings.lexguard_debug,
)

# Enable SQLite foreign key enforcement
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Shared declarative base for all LexGuard models."""
    pass


def init_db() -> None:
    """Create all tables defined on Base.metadata."""
    # Import models so they register with Base.metadata
    import backend.models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency yielding a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
