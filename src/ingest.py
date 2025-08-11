import sqlite3
from typing import Iterable, Tuple

import pandas as pd

DB_PATH = "data/vahan.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            vehicle_category TEXT NOT NULL,
            maker TEXT NOT NULL,
            registrations INTEGER NOT NULL
        )
    """)

    # Check if table already has data
    cursor.execute("SELECT COUNT(*) FROM registrations")
    count = cursor.fetchone()[0]
    if count == 0:
        try:
            records = list(_load_vahan_records("data/vahan.csv"))
            cursor.executemany(
                """
                INSERT INTO registrations (date, vehicle_category, maker, registrations)
                VALUES (?, ?, ?, ?)
                """,
                records,
            )
            print(f"Inserted {len(records)} rows from dataset.")
        except Exception:
            # Fallback to minimal sample data if dataset is missing
            sample_data = [
                ("2025-01-01", "2W", "Honda", 1200),
                ("2025-01-01", "4W", "Maruti", 1500),
                ("2025-02-01", "2W", "Yamaha", 900),
                ("2025-02-01", "4W", "Hyundai", 1300),
                ("2025-03-01", "2W", "Honda", 1400),
                ("2025-03-01", "4W", "Tata", 1100),
                ("2025-04-01", "2W", "Suzuki", 1000),
                ("2025-04-01", "4W", "Maruti", 1600),
                ("2025-05-01", "2W", "Honda", 1500),
                ("2025-05-01", "4W", "Hyundai", 1400),
            ]
            cursor.executemany(
                """
                INSERT INTO registrations (date, vehicle_category, maker, registrations)
                VALUES (?, ?, ?, ?)
                """,
                sample_data,
            )
            print(f"Inserted {len(sample_data)} sample rows.")

    conn.commit()
    conn.close()
    print("Database ready.")


def _load_vahan_records(path: str) -> Iterable[Tuple[str, str, str, int]]:
    """Return iterable of records parsed from the Vahan dataset.

    The expected dataset contains columns: ``date``, ``vehicle_category``,
    ``maker`` and ``registrations``. Any rows missing these fields are
    dropped. This helper uses :func:`pandas.read_csv` to load a CSV
    dataset. If reading fails the caller should handle the exception.
    """

    df = pd.read_csv(path)
    df = df.dropna(subset=["date", "vehicle_category", "maker", "registrations"])
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["registrations"] = pd.to_numeric(df["registrations"], errors="coerce").fillna(0).astype(int)
    return df[["date", "vehicle_category", "maker", "registrations"]].itertuples(index=False, name=None)


if __name__ == "__main__":
    init_db()
