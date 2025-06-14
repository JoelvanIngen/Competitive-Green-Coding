"""
Module responsible for building engine and getting session
"""

from sqlmodel import Session, SQLModel, create_engine

from db import settings

__all__ = ["get_session", "create_db_and_tables"]


SQLITE_FILE_NAME = "database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

POSTGRES_URL = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

CONNECT_ARGS = {"check_same_thread": False}


def build_engine():
    match settings.DB_ENGINE:
        case "postgres":
            url = POSTGRES_URL
        case "sqlite":
            url = SQLITE_URL
        case _:
            raise RuntimeError(f"Unknown database engine {settings.DATABASE_ENGINE}")

    return create_engine(url, connect_args=CONNECT_ARGS)


def create_db_and_tables():
    """Create SQLModel tables."""

    SQLModel.metadata.create_all(engine)


def get_session():
    """Get session to communicate with the underlying database.

    Yields:
        Session: session to communicate with the database
    """

    with Session(engine) as session:
        yield session


engine = build_engine()
