"""
SQLAlchemy engine/session setup. SQLite by default for local dev and the hackathon
demo — swap DATABASE_URL to a Postgres URL (e.g. Render Postgres) for production
without touching any other file.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: yields a DB session and always closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
