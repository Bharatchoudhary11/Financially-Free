# tests/test_app.py
import os
import sqlite3
import pandas as pd
from src.dashboard.app import load_db, compute_monthly_aggs

def test_db_exists():
    assert os.path.exists("data/vahan.db"), "Database file missing!"

def test_table_structure():
    conn = sqlite3.connect("data/vahan.db")
    df = pd.read_sql("SELECT * FROM registrations LIMIT 1", conn)
    conn.close()
    expected_cols = {'date', 'vehicle_category', 'maker', 'registrations'}
    assert expected_cols.issubset(df.columns), "Missing columns in DB"
