import os
import threading
from sqlalchemy import create_engine, text, Enum, Integer, String, Date, Text, Column
from sqlalchemy.orm import declarative_base, sessionmaker

def _build_db_url(db_name: str) -> str:
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"

class Database:
    """Singleton providing a shared SQLAlchemy engine and simple execute API.

    Supports per-database singletons via get_for(db_name).
    """

    _instances = {}
    _lock = threading.Lock()

    def __init__(self, db_name: str):
        self._db_name = db_name
        self._engine = create_engine(_build_db_url(db_name), future=True)
        self._SessionLocal = sessionmaker(bind=self._engine, expire_on_commit=False, future=True)

    @classmethod
    def instance(cls):
        db_name = os.getenv("DB_NAME")
        if not db_name:
            raise RuntimeError("DB_NAME is not set in environment/.env")
        return cls.get_for(db_name)

    @classmethod
    def get_for(cls, db_name: str):
        if db_name not in cls._instances:
            with cls._lock:
                if db_name not in cls._instances:
                    cls._instances[db_name] = cls(db_name)
        return cls._instances[db_name]

    @property
    def engine(self):
        return self._engine

    def session(self):
        return self._SessionLocal()

    def execute(self, sql: str, params: dict | None = None, *, autocommit: bool = False):
        with self._engine.connect() as conn:
            if autocommit:
                conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            result = conn.execute(text(sql), params or {})
            if not autocommit and not result.returns_rows:
                conn.commit()
            return result