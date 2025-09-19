"""
    This is a one-time run script to download the Jeopardy CSV and store it into the Postgres database.
"""

import csv
import io
import re
import requests
import os
import datetime as dt

try:
    # Load .env if python-dotenv is available
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# SQLAlchemy ORM imports
from sqlalchemy import create_engine, text, Enum, Integer, String, Date, Text, Column
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

data_source = "https://raw.githubusercontent.com/russmatney/go-jeopardy/master/JEOPARDY_CSV.csv"

def download_csv(source_url=None):
    """Download the CSV and return its text content (in-memory)."""
    url = source_url or data_source
    print(f"Downloading CSV from: {url}")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    response.encoding = response.encoding or "utf-8"
    return response.text


def filter_entries_by_value_max(content, max_value=1200):
    """Return rows whose Value (e.g., "$400") is <= max_value.

    - Parses the CSV in-memory and normalizes header keys by stripping whitespace.
    - Skips rows with missing or non-numeric Value.
    - Returns a list of dictionaries keyed by normalized headers.
    """
    reader = csv.DictReader(io.StringIO(content))
    results = []

    for row in reader:
        # Normalize keys and values (strip surrounding spaces)
        normalized = { (k.strip() if k is not None else k): (v.strip() if isinstance(v, str) else v) for k, v in row.items() }
        value_str = (normalized.get("Value") or "").strip()

        # Extract digits from something like "$1,200"
        digits = re.sub(r"[^0-9]", "", value_str)
        if not digits:
            continue

        amount = int(digits)
        if amount <= max_value:
            results.append(normalized)

    return results


class Question(Base):
    __tablename__ = "questions"

    # Surrogate primary key for ORM convenience
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Columns as specified (use exact names via Column name parameter)
    show_number = Column("Show Number", Integer, nullable=False)
    air_date = Column("Air Date", Date, nullable=False)
    round = Column("Round", Enum("Jeopardy!", "Double Jeopardy!", "Final Jeopardy!", name="round_enum"), nullable=False)
    category = Column("Category", String(255), nullable=False)
    value = Column("Value", Integer, nullable=True)
    question = Column("Question", Text, nullable=False)
    answer = Column("Answer", Text, nullable=False)


def _build_db_url(db_name: str) -> str:
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"


def create_database_and_questions_table():
    """Create the Postgres database (from .env DB_NAME) and the questions table.

    Assumes connection params via env vars: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT.
    Defaults: postgres/postgres@localhost:5432
    """
    db_name = os.getenv("DB_NAME")
    if not db_name:
        raise RuntimeError("DB_NAME is not set in environment/.env")

    # Connect to default 'postgres' database to create target db if needed
    admin_url = _build_db_url("postgres")
    target_url = _build_db_url(db_name)

    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    print(f"Admin URL: {admin_url}")
    with admin_engine.connect() as conn:
        exists = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": db_name}).scalar() is not None
        if not exists:
            conn.execute(text(f"CREATE DATABASE \"{db_name}\""))
            print(f"Created database: {db_name}")
        else:
            print(f"Database already exists: {db_name}")

    # Create the questions table in the target database
    engine = create_engine(target_url, future=True)
    Base.metadata.create_all(engine, tables=[Question.__table__])
    print("Ensured table 'questions' exists.")


def _get_engine_for_target_db():
    db_name = os.getenv("DB_NAME")
    if not db_name:
        raise RuntimeError("DB_NAME is not set in environment/.env")
    return create_engine(_build_db_url(db_name), future=True)


def _parse_int_value(value_str: str):
    if value_str is None:
        return None
    digits = re.sub(r"[^0-9]", "", value_str)
    if not digits:
        return None
    return int(digits)


def _parse_date(date_str: str):
    # Expecting format YYYY-MM-DD
    try:
        return dt.datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except Exception:
        return None


def persist_questions(filtered_rows):
    """Create and store Question entities from filtered CSV dictionaries.

    filtered_rows: iterable of dicts with keys matching CSV headers
                  ['Show Number',' Air Date',' Round',' Category',' Value',' Question',' Answer']
    """
    engine = _get_engine_for_target_db()
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)

    to_persist = []
    for row in filtered_rows:
        # Normalize keys (strip spaces) as done in filter_entries_by_value_max
        normalized = { (k.strip() if k is not None else k): (v.strip() if isinstance(v, str) else v) for k, v in row.items() }

        show_number = None
        try:
            show_number = int(normalized.get("Show Number")) if normalized.get("Show Number") else None
        except Exception:
            show_number = None

        air_date = _parse_date(normalized.get("Air Date") or "")
        round_value = normalized.get("Round") or None
        category = normalized.get("Category") or None
        value_int = _parse_int_value(normalized.get("Value"))
        question_text = normalized.get("Question") or None
        answer_text = normalized.get("Answer") or None

        # Basic validation: required fields
        if not (show_number and air_date and round_value and category and question_text and answer_text):
            continue

        to_persist.append(
            Question(
                show_number=show_number,
                air_date=air_date,
                round=round_value,
                category=category,
                value=value_int,
                question=question_text,
                answer=answer_text,
            )
        )

    if not to_persist:
        print("No valid question rows to persist.")
        return 0

    with SessionLocal() as session:
        session.add_all(to_persist)
        session.commit()
    print(f"Persisted {len(to_persist)} question rows.")
    return len(to_persist)


if __name__ == "__main__":
    data = download_csv()
    data_filtered = filter_entries_by_value_max(data, max_value=1200)
    create_database_and_questions_table()
    persist_questions(data_filtered)