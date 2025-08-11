import os
import sqlite3
import pandas as pd
import sys

# Ensure the project root is on the path so ``src`` can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingest import init_db, DB_PATH


def setup_module(module):
    """Ensure the sample database exists for the tests."""
    init_db()


def teardown_module(module):
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_db_exists():
    assert os.path.exists(DB_PATH), "Database file missing!"


def test_table_structure():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM registrations LIMIT 1", conn)
    conn.close()
    expected_cols = {"date", "vehicle_category", "maker", "registrations"}
    assert expected_cols.issubset(df.columns), "Missing columns in DB"

