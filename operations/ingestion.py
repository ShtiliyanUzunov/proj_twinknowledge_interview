"""
    This is a one-time run script to download the Jeopardy CSV and store it into the Postgres database.
"""

import csv
import io
import re
import requests
import os
import threading
import datetime as dt

try:
    # Load .env if python-dotenv is available
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# SQLAlchemy ORM imports
from sqlalchemy import text, Enum, Integer, String, Date, Text, Column
from sqlalchemy.orm import declarative_base, sessionmaker
from persistence.database import Database
from persistence.question import Base, Question

data_source = "https://raw.githubusercontent.com/russmatney/go-jeopardy/master/JEOPARDY_CSV.csv"

def download_csv(source_url=None):
    url = source_url or data_source
    print(f"Downloading CSV from: {url}")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    response.encoding = response.encoding or "utf-8"
    return response.text


def filter_entries_by_value_max(content, max_value=1200):
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


def create_database_and_questions_table():
    db_name = os.getenv("DB_NAME")
    if not db_name:
        raise RuntimeError("DB_NAME is not set in environment/.env")

    # Connect to default 'postgres' database to create target db if needed
    admin_db = Database.get_for("postgres")
    exists = admin_db.execute(
        "SELECT 1 FROM pg_database WHERE datname = :name", {"name": db_name}
    ).scalar() is not None
    if not exists:
        admin_db.execute(f"CREATE DATABASE \"{db_name}\"", autocommit=True)
        print(f"Created database: {db_name}")
    else:
        print(f"Database already exists: {db_name}")

    # Create the questions table in the target database using the singleton engine
    engine = Database.instance().engine
    Base.metadata.create_all(engine, tables=[Question.__table__])
    print("Ensured table 'questions' exists.")


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

    with Database.instance().session() as session:
        session.add_all(to_persist)
        session.commit()
    print(f"Persisted {len(to_persist)} question rows.")
    return len(to_persist)


if __name__ == "__main__":
    data = download_csv()
    data_filtered = filter_entries_by_value_max(data, max_value=1200)
    create_database_and_questions_table()
    persist_questions(data_filtered)