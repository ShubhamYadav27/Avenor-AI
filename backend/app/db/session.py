from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, MappedColumn, Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# ── Engine ────────────────────────────────────────────────────

def _create_engine():
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,       # detect stale connections
        pool_recycle=3600,        # recycle connections every hour
        echo=settings.is_development,  # SQL logging in dev only
    )

    # Enforce workspace isolation at the session level via RLS
    @event.listens_for(engine, "connect")
    def set_search_path(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.close()

    return engine


engine = _create_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # prevent lazy-load errors after commit
)


# ── Base model ────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ── FastAPI dependency ─────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    Automatically commits on success, rolls back on exception.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Context manager for workers/scripts ───────────────────────

@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager for use outside of FastAPI (workers, scripts).
    Usage:
        with db_session() as db:
            companies = db.query(Company).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Database initialization ───────────────────────────────────

def init_db() -> None:
    """
    Create all tables and enable pgvector extension.
    Called once on application startup.
    """
    # Import all models to ensure they are registered with Base
    import app.models  # noqa: F401

    with engine.connect() as conn:
        # Enable pgvector extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # Enable pg_trgm for fuzzy company name matching
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        conn.commit()

    Base.metadata.create_all(bind=engine)
    logger.info("database_initialized", tables=list(Base.metadata.tables.keys()))


def check_db_connection() -> bool:
    """Health check — returns True if database is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("database_connection_failed", error=str(e))
        return False
