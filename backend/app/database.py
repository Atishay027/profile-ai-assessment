from datetime import timezone

from sqlalchemy import DateTime, create_engine, types
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class UTCDateTime(types.TypeDecorator):
    """DateTime that round-trips as tz-aware UTC even on SQLite, which drops tzinfo on read.

    Stores naive UTC on write, re-attaches UTC tzinfo on read so comparisons against
    now_utc() (always tz-aware) never raise 'can't compare offset-naive and offset-aware'.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
